# Bun 测试运行器源码架构分析

> 深入分析 `bun test` 的实现原理，包括测试发现、执行、快照、覆盖率等核心机制。

---

## 一、测试运行器架构概览

Bun 的测试运行器是一个**内置的 Jest 兼容测试框架**，使用 Zig 实现核心引擎，提供与 Jest 几乎相同的 API，但执行速度大幅提升。

```
┌─────────────────────────────────────────────────────────────┐
│                    bun test 流程                            │
│                                                             │
│  输入: bun test [pattern] [--coverage]                      │
│                                                             │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 1. 测试发现 (Discovery)                              │   │
│  │    - 扫描文件匹配 pattern                            │   │
│  │    - 识别 *.test.{ts,js,tsx,jsx}                     │   │
│  │    - 识别 *.spec.{ts,js,tsx,jsx}                     │   │
│  └─────────────────────────────────────────────────────┘   │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 2. 测试加载 (Load)                                   │   │
│  │    - 转译 TS/JSX                                     │   │
│  │    - 注册 test/describe 钩子                         │   │
│  └─────────────────────────────────────────────────────┘   │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 3. 测试执行 (Execute)                                │   │
│  │    - 并行执行测试文件                                │   │
│  │    - 每个文件独立 JSC 上下文                         │   │
│  │    - 支持并发/串行模式                               │   │
│  └─────────────────────────────────────────────────────┘   │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 4. 结果报告 (Report)                                 │   │
│  │    - 快照对比                                        │   │
│  │    - 覆盖率收集                                      │   │
│  │    - 输出测试报告                                    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、测试发现机制

### 2.1 文件扫描

Bun 使用高效的文件系统扫描发现测试文件：

```zig
// 默认测试文件模式
const default_patterns = [_][]const u8{
    "**/*.test.{ts,tsx,js,jsx}",
    "**/*.spec.{ts,tsx,js,jsx}",
};

// 扫描逻辑
pub fn discoverTests(
    allocator: Allocator,
    patterns: []const []const u8,
) ![]TestFile {
    var results = std.ArrayList(TestFile).init(allocator);
    
    for (patterns) |pattern| {
        var glob = try Glob.init(pattern);
        var iter = glob.walk(".");
        while (try iter.next()) |entry| {
            try results.append(.{
                .path = entry.path,
                .size = entry.size,
            });
        }
    }
    
    return results.toOwnedSlice();
}
```

### 2.2 测试文件过滤

支持多种过滤方式：

```bash
# 按文件名过滤
bun test foo          # 匹配包含 "foo" 的文件

# 按测试名过滤
bun test --test-name-pattern="should handle"

# 按路径过滤
bun test src/utils/
```

---

## 三、测试执行模型

### 3.1 并行执行架构

Bun 的测试执行高度并行化：

```
主进程 (Zig)
    │
    ├──→ 发现 N 个测试文件
    │
    └──→ 启动 M 个工作线程（默认 CPU 核心数）
            │
            ├──→ Worker 1: 执行 test-a.test.ts
            │       ├──→ 创建独立 JSC VM
            │       ├──→ 加载并执行测试
            │       └──→ 返回结果
            │
            ├──→ Worker 2: 执行 test-b.test.ts
            │       └──→ ...
            │
            └──→ Worker M: 执行 test-m.test.ts
                    └──→ ...
```

### 3.2 每个文件的隔离

每个测试文件在独立的 JSC 上下文中执行，确保测试隔离：

```zig
// 为每个测试文件创建新的 JSGlobalObject
pub fn runTestFile(path: []const u8) TestResult {
    // 创建新的 JSC VM
    var vm = JSC.VM.create();
    defer vm.destroy();
    
    // 创建全局对象
    var global = ZigGlobalObject.create(vm);
    
    // 注册测试钩子
    global.put(test_fn);
    global.put(describe_fn);
    global.put(expect_fn);
    
    // 执行测试文件
    const result = global.evaluateScript(path);
    
    return collectResults(global);
}
```

### 3.3 生命周期钩子

支持完整的 Jest 风格生命周期：

```javascript
// 文件级别
beforeAll(() => {});
afterAll(() => {});

// 测试级别
beforeEach(() => {});
afterEach(() => {});

// 测试定义
describe('suite', () => {
  test('case', () => {
    expect(true).toBe(true);
  });
});
```

---

## 四、Expect API 实现

### 4.1 Matcher 系统

Bun 实现了 Jest 的 expect API，使用 Zig 编写核心 matcher：

```zig
// src/bun.js/test/
pub const Expect = struct {
    value: JSC.JSValue,
    is_not: bool,
    
    pub fn toBe(self: *Expect, expected: JSC.JSValue) !void {
        const actual = self.value;
        
        // 严格相等比较（SameValue 语义）
        if (actual.strictEquals(expected) == self.is_not) {
            return error.ExpectationFailed;
        }
    }
    
    pub fn toEqual(self: *Expect, expected: JSC.JSValue) !void {
        // 深度相等比较
        const result = try deepEqual(self.value, expected);
        if (result == self.is_not) {
            return error.ExpectationFailed;
        }
    }
    
    pub fn toThrow(self: *Expect, expected: ?JSC.JSValue) !void {
        // 异常捕获和匹配
        // ...
    }
};
```

### 4.2 支持的 Matchers

| Matcher | 说明 | 实现位置 |
|---------|------|---------|
| `toBe` | 严格相等 | Zig 原生 |
| `toEqual` | 深度相等 | Zig 原生 |
| `toBeTruthy/toBeFalsy` | 布尔转换 | Zig 原生 |
| `toBeNull/toBeUndefined` | 空值检查 | Zig 原生 |
| `toContain` | 包含检查 | Zig 原生 |
| `toMatch` | 正则匹配 | Zig 原生 |
| `toThrow` | 异常捕获 | Zig 原生 |
| `toHaveBeenCalled` | Mock 检查 | Zig 原生 |
| `toMatchSnapshot` | 快照对比 | Zig + 文件 I/O |

---

## 五、快照测试

### 5.1 快照文件格式

Bun 使用 `.snap` 文件存储快照：

```
__snapshots__/
└── my-test.test.ts.snap

// Jest 格式（Bun 兼容）
// Bun Snapshot v1, https://goo.gl/fbAQLP

exports[`should render correctly 1`] = `
<div>
  <h1>Hello</h1>
</div>
`;
```

### 5.2 快照更新流程

```
测试执行
    │
    ├──→ 遇到 toMatchSnapshot()
    │       │
    │       ├──→ 快照文件存在？
    │       │       ├──→ 是：对比当前值与快照
    │       │       │       ├──→ 匹配：通过
    │       │       │       └──→ 不匹配：失败
    │       │       │
    │       └──→ 否：创建新快照
    │
    └──→ bun test --update-snapshots
            └──→ 强制更新所有快照
```

---

## 六、代码覆盖率

### 6.1 覆盖率收集

Bun 使用 **JSC 内置的覆盖率 API** 收集代码覆盖率：

```
测试文件执行
    │
    └──→ JSC VM 启用覆盖率跟踪
            │
            ├──→ 记录每个语句的执行次数
            ├──→ 记录每个分支的走向
            └──→ 记录每个函数的调用

测试完成后
    │
    └──→ 收集覆盖率数据
            │
            ├──→ 生成 LCOV 报告
            ├──→ 生成 HTML 报告
            └──→ 输出文本摘要
```

### 6.2 覆盖率配置

```toml
# bunfig.toml
[test]
coverage = true
coverageDirectory = "coverage"
coverageReporter = ["text", "lcov"]
coverageSkipTestFiles = true
coveragePathIgnorePatterns = [
  "**/node_modules/**",
  "**/dist/**",
]
```

### 6.3 覆盖率报告格式

Bun 支持多种覆盖率报告格式：

| 格式 | 用途 |
|------|------|
| `text` | 终端输出摘要 |
| `lcov` | 与 Coveralls/Codecov 集成 |
| `html` | 可视化报告 |

---

## 七、Mock 系统

### 7.1 函数 Mock

Bun 提供与 Jest 兼容的 mock 函数：

```javascript
import { jest, test, expect } from "bun:test";

const mockFn = jest.fn();
mockFn("arg1", "arg2");

expect(mockFn).toHaveBeenCalledTimes(1);
expect(mockFn).toHaveBeenCalledWith("arg1", "arg2");
```

### 7.2 模块 Mock

支持使用 `jest.mock` 模拟模块：

```javascript
jest.mock("./my-module", () => ({
  myFunction: () => "mocked",
}));
```

### 7.3 Timer Mock

支持模拟定时器：

```javascript
jest.useFakeTimers();

// 快进时间
jest.advanceTimersByTime(1000);

// 运行所有定时器
jest.runAllTimers();
```

---

## 八、测试报告器

### 8.1 内置报告器

Bun 提供多种测试报告格式：

```toml
# bunfig.toml
[test.reporter]
# 紧凑的点报告器
dots = true

# JUnit XML 报告（CI 集成）
[test.reporter.junit]
enabled = true
output = "./test-results.xml"
```

### 8.2 报告器类型

| 报告器 | 说明 | 适用场景 |
|--------|------|---------|
| 默认报告器 | 详细的测试列表 | 开发调试 |
| Dots 报告器 | 每个测试一个点 | CI 环境 |
| JUnit XML | 标准 XML 格式 | Jenkins/Azure DevOps |

---

## 九、核心源码文件

| 功能 | 核心文件 |
|------|---------|
| 测试主流程 | `src/cli/test_command.zig` |
| 测试框架 | `src/bun.js/test/` |
| Expect API | `src/bun.js/test/expect.zig` |
| Mock 系统 | `src/bun.js/test/mock.zig` |
| 快照测试 | `src/bun.js/test/snapshot.zig` |
| 覆盖率 | `src/bun.js/test/coverage.zig` |
| 报告器 | `src/bun.js/test/reporter.zig` |
| 测试运行 | `src/bun.js/test/jest.zig` |

---

## 十、与 Jest 的对比

| 维度 | Jest | Bun Test |
|------|------|----------|
| **实现语言** | JavaScript (Node.js) | Zig + JSC |
| **启动时间** | 慢（需加载大量 JS） | 快（原生实现） |
| **执行速度** | 快 | 更快（~10x） |
| **内存占用** | 高 | 更低 |
| **API 兼容** | 标准 | Jest 兼容 |
| **TypeScript** | 需 ts-jest | 原生支持 |
| **覆盖率** | Istanbul | 内置 |
| **快照** | 支持 | 兼容 Jest 格式 |
| **Mock** | 完善 | 核心功能 |
| **DOM 测试** | jsdom | 支持 |

---

## 十一、参考资源

- [Bun Test Docs](https://bun.sh/docs/test)
- [Bun Test Writing](https://bun.sh/docs/test/writing-tests)
- [Bun Test Coverage](https://bun.sh/docs/test/code-coverage)
- [Jest Docs](https://jestjs.io/)
