# Soul Market 实际提取候选

Market 已从实际 Core `move/soulidity_v1/sources/market.move` 迁为独立 `SoulidityMarket` package、`soulidity_market::market` 模块。这里是源码提取候选与冻结构建依赖，不是部署声明，也不是整个十仓拆分或 schema 解耦完成。

## 已验证结果

- 独立生产 build：通过。冻结 Core **实际移除** `sources/market.move`，其生产源码没有反向 import Market。
- 不同地址跨包 VM：**44/44 通过**，Core `0x107`、Market `0x10a`，CLI 默认 gas budget。
- 原 `market_tests.move` 15 个测试全部保留；新增旧 Core Market role 不可授权新 Market；保留 16 个独立门控、5 个全局门控、6 个原 Collection Market 测试并新增成员缺失反例。
- Market 生产字节码 8614 字节，SHA256 `c4cdde40f0b0fa78e76c016d6857ab2cdf2350f1315922ff2d697925146bf51e`。
- 实际输入九包 52 份生产 Move 源码、manifest/已有锁原 SHA 已冻结；actual 源码与锁读回 SHA 未变。

最终证据在 `../evidence/verification.json`、`../evidence/production-build-final.log`、`../evidence/market-tests-final.log`；迁移差异在 `../evidence/market-source.diff`。前四轮失败日志按原样保留，未把编译失败当业务反例。

## 生产变更及保持义务

只改模块 namespace，并将两处 Core 私有 `collection::assert_member` 调用改为本模块私有 helper，读取现有 public API，严格保留三项检查：Soul protocol 等于 Collection protocol、Soul collection ID 等于 Collection ID、Collection 成员表包含 Soul ID。原 abort code 3 保留；错误 location 随新模块变为 `soulidity_market::market`。没有新增公开资产/UID/Cap 借用。

保留真实 Soul/Item/Control list/cancel/buy、报价和 revision CAS、不可变 resale 经济权利、Collection 当前权利持有人重报价及分项 ceil 义务、原对象 ID、授权清理、递归 Vault handover、原资金与库存、暂停/禁用后取消/收入退出、permissionless terminal cleanup 和精确事件/收据。生产 `register` 仍要求 Admin + disabled Config/CAS + Publisher + 最新 UpgradeCap；私有 `MarketAuthority1` 与 `MarketRevision3` 仍在 Market 内构造和消耗。

新模块没有复用旧 Market 类型或调用。Root production bytecode 只有新 Market；依赖 Core 不再含旧 Market bytecode。

## 最小测试适配

原测试跨包编译真实发现 `EC04001`：`catalog::lifecycle` 私有调用和迁到 Market 的 fixture 内部 issuer/native/player 私有调用。

- 测试暂停改用已有公开 `release::pause`。
- Core `tests/fixtures.move` 原内容保留，追加泛型测试 setup，在 Config 激活前绑定新 Market role；Core 私有发行与 player 调用继续留在 Core 的 `#[test_only]` fixture。
- Market 唯一新增 helper 是 `#[test_only] setup_for_testing`，仅在本模块构造私有 witness 并交给 Core 测试桥。所有依赖生产源码与权限未改。
- 改桥前后 Market 生产字节码 SHA 完全相同，测试桥不进入生产制品。

## 当前业务依赖与未完成项

Market 仍直接使用 Core Catalog Product/Control、Core Collection、Application Character/Vault/resale、Standard Soul、Model Item/policy、Foundation Config/经济角色注册；Core 的完整临时冻结依赖图还包含 Native/Content/Visual/Community。这是可生产编译的真实独立 Market 包，不是无业务依赖的协议内核。

下一段必须在保持用户已确认行为下解耦 Catalog/Collection schema 与边界适配，并联动 consumers、SDK 及明确的 fresh package 发布/role 注册候选；本增量尚未进行 schema 解耦、迁移、发布、签名或消费者切换。

## 复验

在 `repository-extraction` 目录执行 `python3 verify_market_extraction.py --sui /Users/naoer/.codex/worktrees/soul-dof-v1-rebuild/soulidity/output/contract-rebuild/local-ptb-2026-10-08/tooling/sui`。脚本使用这里的冻结生产输入及测试桥，生产和跨包测试输出写入 `evidence/replay`。

回滚：移除此隔离提取候选即可；actual 源码、锁、CURRENT、钱包、节点、DB、历史 receipts 和原队列未修改。未 commit/push/创建远程仓库。
