# Market 提取源码增量交接

工作树 `/Users/naoer/.codex/worktrees/ecosystem-market-extraction/soulidity`，仅新增 `repository-extraction/**`；真实输入 `/Users/naoer/.codex/worktrees/soul-dof-v1-rebuild/soulidity` 保持只读。

## 本增量已实现并验证

- 新包：`soul-market/move/soulidity_market/Move.toml`、`sources/market.move`、4 个测试模块。
- 九包 52 份原生产源冻结在 `dependencies/`；Core 副本明确移除 Market，Core 剩余生产源均逐字不变。
- 独立生产 build exit 0；`evidence/production-build-final.log`。Market bytecode 8614B，SHA256 `c4cdde40f0b0fa78e76c016d6857ab2cdf2350f1315922ff2d697925146bf51e`。
- Core `0x107` / Market `0x10a`，VM default budget 44/44 PASS；`evidence/market-tests-final.log`。原 Market 15 测试保留，独立门控16、全局门控5、Collection Market7，加旧Core角色不能授权新Market1，共44。
- private Collection membership 两处调用→私有等价三项 public getter helper，abort code3；只读身份校验，无新资产/UID/Cap 暴露。
- 原 Soul/Item/Control 生产交易、Vault/资金、Collection/转售和私有经济 role-witness 均保留。
- test-only Core fixture 泛型桥，私有 issuance/player 留在 Core；Market私有witness只经test-only setup构造。生产 bytecode 与桥前同 SHA。

## 失败记录与适配

初始 build 的 package alias 不符（已用真实 soulidity_v1 键修正）；test r1 真实 EC04001（catalog lifecycle），r2 真实 EC04001（搬到Market的fixture私有issuance/native）；r3 包含测试桥局部保留字错误与private player调用，r4新增测试的泛型token/返回effects错误。四轮失败日志保留，未当作业务安全PASS。最终44业务测试在不同地址和真实 private visibility 下通过；公开release::pause和Core test-only桥是实际修复。

## 下一段

该包仍有业务 schema 依赖：Core Catalog Product/Control 与 Collection、Application Character/Vault/resale、Standard Soul、Model Item/policy、Foundation Config及 role registration。独立 package 生产构建已成，但 schema 解耦、消费者/SDK 切换、新部署/role注册与完整十仓独立发布未完成。沿用户原“按模块实际拆仓”目标继续，不能退回 creation gate 当主线，也不能以本增量关闭完整重构目标。

交接给主协调任务集成源码和原卡阶段证据，并安排只读核验。当前所有原Owner、157原记录和CURRENT continuation未动。

## 产品工程评审记录（附原任务，不新建看板）

- 用户结果：Market 真正成为独立包，保留原交易/资金/退出行为。
- 当前阶段/状态：Code、Build、Test 已通过本增量；Release/Deploy/Adopted 待核验。独立复核由主任务安排。
- 手册版本：1.0（2026-10-06）；适用1–5、6支付精度、7、8.3/8.4、9、12；OPERATING_MODEL 第8节。
- Owner/验收及运行：沿用原任务已有Owner与SENTINEL/HARBOR职责，本增量没有重分配。
- 资产/权利/资金：Listing DOF实际托管Soul/Item/Control；Coin payment原路经济settle；Collection当前holder和snapshot/quote参与结算；原Vault资金资产与权限代际随原Soul交接。
- 权力：seller只能取消自己的LIVE Listing；任意wallet可删除无实际escrow的terminal receipt；买家绑定quote和exact Coin；Config Admin/CAS + Publisher/最新UpgradeCap注册新Market role。没有新增多签、timelock或immutability声明。
- Sui核验：生产跨包build、private visibility、独立role误用反例、ID/库存/资金/退出和暂停门控通过VM；实际PTB及链上readback未运行。
- 金融模型：保持已有费率/ceil/floor/收据，无新增金融产品或定价决策；Collection四收款方原测试通过。
- EVM：不适用，本增量为Sui Move。
- 治理/升级/锁：生产role义务保留；真实Publisher/Cap注册和升级控制读回待下一发布候选核验；测试bootstrap不证明生产已注册。
- 审计：内部源码提取与VM不等于外部审计，独立复核待协调者。
- 部署/签名/资金/remote/Git：均未执行；无消费者切换。
- 退出/恢复：VM验证取消、permissionless terminal cleanup、暂停/双lane禁用后原资产ID与已结算收入退出；回滚移除隔离提取候选，actual与历史链状态没有变化。
- 证据：`evidence/verification.json`、source-freeze、frozen-production-sources、market-source.diff、最终build/test log。

复验脚本 `verify_market_extraction.py` 的prepare-only已验证；最终build/test是在上列固定CLI直接运行，prepare-only没有被算成执行测试。
