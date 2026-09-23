# 全目录知识与接口路由审查

覆盖 126 个来源。`knowledge_status` 表示能否进入自有模式仓；`route_modes` 表示 Agent 可走的实际路径。提供方接口始终由用户自己的账号连接，本服务不代调。

## 汇总

- 自有仓判定：alias 2, candidate 31, included 6, included-scoped 1, needs-source-verification 1, out-of-scope 9, reference-only 63, rights-review 13
- 提供方接口判定：needs-live-recheck 9, none 97, provider-documented 16, unofficial-not-routed 4
- 自有模式在 `knowledge/patterns/`；来源登记在 `index.csv`。专有站点只提供自写摘要、事实分类和原站链接。

## 逐条决定

| ID | 来源 | 自有仓 | 路由 | 提供方状态 | 依据 |
|---|---|---|---|---|---|
| 001 | Ambient CSS | included | self-pattern; source-link | none | An authored pattern with source attribution is in the knowledge repository. |
| 002 | DESIGN.md | included | self-pattern; source-link | none | An authored pattern with source attribution is in the knowledge repository. |
| 003 | Impeccable | included | self-pattern; source-link | none | An authored pattern with source attribution is in the knowledge repository. |
| 004 | Diagram Design | included | self-pattern; source-link | none | An authored pattern with source attribution is in the knowledge repository. |
| 005 | YI TUO HUB STUDIO | out-of-scope | source-link | none | Adjacent topic; not part of default front-end pattern search. |
| 006 | IP as Logo | candidate | source-link | none | Permissive source is available for text-only pattern extraction after review. |
| 007 | Beautify GitHub README | candidate | source-link | none | Permissive source is available for text-only pattern extraction after review. |
| 008 | models.dev | out-of-scope | source-link | none | Adjacent topic; not part of default front-end pattern search. |
| 009 | Agent Reach | out-of-scope | source-link | none | Adjacent topic; not part of default front-end pattern search. |
| 010 | Developer Portfolios | rights-review | source-link | none | License scope or permission needs case-by-case review before ingestion. |
| 011 | .NET Agent Skills | out-of-scope | source-link | none | Adjacent topic; not part of default front-end pattern search. |
| 012 | Appshots | reference-only | source-link | unofficial-not-routed | Proprietary source remains an authored summary and source link. Unofficial wrapper is not an automatic provider route. |
| 013 | ScreensDesign | reference-only | provider-direct; source-link | provider-documented | Proprietary source remains an authored summary and source link. |
| 014 | Refero | reference-only | provider-direct; source-link | provider-documented | Proprietary source remains an authored summary and source link. |
| 015 | Page Flows | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 016 | Mobbin | reference-only | provider-direct; source-link | provider-documented | Proprietary source remains an authored summary and source link. |
| 017 | Gummble | reference-only | provider-direct; source-link | provider-documented | Proprietary source remains an authored summary and source link. |
| 018 | CollectUI | reference-only | source-link | unofficial-not-routed | Proprietary source remains an authored summary and source link. Unofficial wrapper is not an automatic provider route. |
| 019 | Revyl | out-of-scope | provider-direct; source-link | needs-live-recheck | Adjacent topic; not part of default front-end pattern search. Provider endpoint needs current setup/terms verification. |
| 020 | Skills For Real Engineers | out-of-scope | source-link | none | Adjacent topic; not part of default front-end pattern search. |
| 021 | Neuform | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 022 | TypeUI | candidate | provider-direct; source-link | needs-live-recheck | Permissive source is available for text-only pattern extraction after review. Provider endpoint needs current setup/terms verification. |
| 023 | Aura | reference-only | provider-direct; source-link | needs-live-recheck | Proprietary source remains an authored summary and source link. Provider endpoint needs current setup/terms verification. |
| 024 | DESIGNMD (Hyperbrowser) | reference-only | provider-direct; source-link | provider-documented | Proprietary source remains an authored summary and source link. |
| 025 | designmd.supply | candidate | provider-direct; source-link | needs-live-recheck | Permissive source is available for text-only pattern extraction after review. Provider endpoint needs current setup/terms verification. |
| 026 | OpenDesign | candidate | source-link | none | Permissive source is available for text-only pattern extraction after review. |
| 027 | DesignMD (designmd.me) | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 028 | Spectrum UI | candidate | source-link | none | Permissive source is available for text-only pattern extraction after review. |
| 029 | Footer | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 030 | ObsidianUI | candidate | source-link | none | Permissive source is available for text-only pattern extraction after review. |
| 031 | DialKit | candidate | source-link | none | Permissive source is available for text-only pattern extraction after review. |
| 032 | liquid-glass | candidate | source-link | none | Permissive source is available for text-only pattern extraction after review. |
| 033 | Screenshot to Code | candidate | source-link | none | Permissive source is available for text-only pattern extraction after review. |
| 034 | UI SFX | candidate | source-link | none | Permissive source is available for text-only pattern extraction after review. |
| 035 | thinking-orbs | candidate | source-link | none | Permissive source is available for text-only pattern extraction after review. |
| 036 | Typeface (Fontr) | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 037 | VibeUI | rights-review | source-link | none | License scope or permission needs case-by-case review before ingestion. |
| 038 | Godly (now Recent) | alias | redirect-item | none | Legacy address; use the canonical item. |
| 039 | Awwwards | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 040 | Cosmos | reference-only | source-link | unofficial-not-routed | Proprietary source remains an authored summary and source link. Unofficial wrapper is not an automatic provider route. |
| 041 | Curated Design | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 042 | Design Spells | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 043 | 60fps | reference-only | provider-direct; source-link | needs-live-recheck | Proprietary source remains an authored summary and source link. Provider endpoint needs current setup/terms verification. |
| 044 | Supahero | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 045 | Saaspo | reference-only | source-link | unofficial-not-routed | Proprietary source remains an authored summary and source link. Unofficial wrapper is not an automatic provider route. |
| 046 | Layers | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 047 | Minimal Gallery | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 048 | MNMM | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 049 | Search System | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 050 | Rebrand Gallery | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 051 | Seesaw | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 052 | Same Energy | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 053 | Spiral (SOOT) | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 054 | Game UI Database | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 055 | Interface In Game | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 056 | HUDs and GUIs | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 057 | Pinterest | reference-only | provider-direct; source-link | provider-documented | Proprietary source remains an authored summary and source link. |
| 058 | Loadmo.re | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 059 | Libraries.dev | candidate | source-link | none | Permissive source is available for text-only pattern extraction after review. |
| 060 | Transitions.dev | rights-review | source-link | none | License scope or permission needs case-by-case review before ingestion. |
| 061 | Astryx | included | self-pattern; provider-direct; source-link | provider-documented | An authored pattern with source attribution is in the knowledge repository. |
| 062 | beUI | candidate | provider-direct; source-link | provider-documented | Permissive source is available for text-only pattern extraction after review. |
| 063 | coss ui | included-scoped | self-pattern; source-link | none | Only the documented MIT subtree informs the authored pattern. |
| 064 | 21st | reference-only | provider-direct; source-link | provider-documented | Proprietary source remains an authored summary and source link. |
| 065 | Beautiful UI | rights-review | source-link | none | License scope or permission needs case-by-case review before ingestion. |
| 066 | Rare UI | candidate | source-link | none | Permissive source is available for text-only pattern extraction after review. |
| 067 | MotionSites AI | reference-only | provider-direct; source-link | provider-documented | Proprietary source remains an authored summary and source link. |
| 068 | Neobrutalism | candidate | source-link | none | Permissive source is available for text-only pattern extraction after review. |
| 069 | React Bits | rights-review | source-link | none | License scope or permission needs case-by-case review before ingestion. |
| 070 | Kokonut UI | candidate | source-link | none | Permissive source is available for text-only pattern extraction after review. |
| 071 | Stackzero Commerce UI | included | self-pattern; provider-direct; source-link | provider-documented | An authored pattern with source attribution is in the knowledge repository. |
| 072 | Fancy Components | candidate | source-link | none | Permissive source is available for text-only pattern extraction after review. |
| 073 | Great UI | rights-review | source-link | none | License scope or permission needs case-by-case review before ingestion. |
| 074 | The Component Gallery | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 075 | Number Flow | candidate | source-link | none | Permissive source is available for text-only pattern extraction after review. |
| 076 | Cursify | rights-review | source-link | none | License scope or permission needs case-by-case review before ingestion. |
| 077 | Motion Primitives | candidate | source-link | none | Permissive source is available for text-only pattern extraction after review. |
| 078 | Pryzm | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 079 | Textures | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 080 | Holosticker | candidate | source-link | none | Permissive source is available for text-only pattern extraction after review. |
| 081 | Shadertoy | reference-only | provider-direct; source-link | provider-documented | Proprietary source remains an authored summary and source link. |
| 082 | Unicorn Studio | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 083 | cables.gl | candidate | source-link | none | Permissive source is available for text-only pattern extraction after review. |
| 084 | TSL Graph | rights-review | source-link | none | License scope or permission needs case-by-case review before ingestion. |
| 085 | Derivative TouchDesigner | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 086 | Nodes.io | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 087 | Shaderfrog | candidate | source-link | none | Permissive source is available for text-only pattern extraction after review. |
| 088 | Inspora | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 089 | Modulify | reference-only | provider-direct; source-link | needs-live-recheck | Proprietary source remains an authored summary and source link. Provider endpoint needs current setup/terms verification. |
| 090 | Ikonik | rights-review | source-link | none | License scope or permission needs case-by-case review before ingestion. |
| 091 | Wonderlist | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 092 | Motion (motionin.design) | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 093 | Bencho | needs-source-verification | source-link | none | Permissive license recorded, but source is not locally archived. |
| 094 | Kobra | reference-only | provider-direct; source-link | provider-documented | Proprietary source remains an authored summary and source link. |
| 095 | Logosystem | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 096 | Siteinspire | reference-only | provider-direct; source-link | needs-live-recheck | Proprietary source remains an authored summary and source link. Provider endpoint needs current setup/terms verification. |
| 097 | 404s.design | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 098 | Detail | candidate | source-link | none | Permissive source is available for text-only pattern extraction after review. |
| 099 | pen.dev | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 100 | Kombai Selects | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 101 | UI Skills | candidate | provider-direct; source-link | provider-documented | Permissive source is available for text-only pattern extraction after review. |
| 102 | GetLayers AI | reference-only | provider-direct; source-link | provider-documented | Proprietary source remains an authored summary and source link. |
| 103 | CTA.gallery | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 104 | Recent | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 105 | Post.Design | out-of-scope | source-link | none | Adjacent topic; not part of default front-end pattern search. |
| 106 | Navbar Gallery | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 107 | AquaInkGL | rights-review | source-link | none | License scope or permission needs case-by-case review before ingestion. |
| 108 | shadcn/ui | candidate | source-link | none | Permissive source is available for text-only pattern extraction after review. |
| 109 | Reelfolio | out-of-scope | provider-direct; source-link | needs-live-recheck | Adjacent topic; not part of default front-end pattern search. Provider endpoint needs current setup/terms verification. |
| 110 | SaaSFrame | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 111 | Aceternity UI | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 112 | Rewamp UI | rights-review | source-link | none | License scope or permission needs case-by-case review before ingestion. |
| 113 | Built by Designers | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 114 | Oxygen UI | rights-review | source-link | none | License scope or permission needs case-by-case review before ingestion. |
| 115 | Arise UI | candidate | source-link | none | Permissive source is available for text-only pattern extraction after review. |
| 116 | Toggles.dev | candidate | source-link | none | Permissive source is available for text-only pattern extraction after review. |
| 117 | Shoogle | reference-only | provider-direct; source-link | needs-live-recheck | Proprietary source remains an authored summary and source link. Provider endpoint needs current setup/terms verification. |
| 118 | Wedoflow | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 119 | closeit.fast | out-of-scope | source-link | none | Adjacent topic; not part of default front-end pattern search. |
| 120 | Uiverse | candidate | source-link | none | Permissive source is available for text-only pattern extraction after review. |
| 121 | useAnimations | rights-review | source-link | none | License scope or permission needs case-by-case review before ingestion. |
| 122 | Iconoir | candidate | source-link | none | Permissive source is available for text-only pattern extraction after review. |
| 123 | Craftwork | reference-only | provider-direct; source-link | provider-documented | Proprietary source remains an authored summary and source link. |
| 124 | Design Vault (now ScreensDesign) | alias | redirect-item | none | Legacy address; use the canonical item. |
| 125 | AnimatedIcons.co | reference-only | source-link | none | Proprietary source remains an authored summary and source link. |
| 126 | Plasma UI | candidate | source-link | none | Permissive source is available for text-only pattern extraction after review. |
