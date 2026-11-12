"""Generate 2381 content: 5 industry chains x 6-8 links, JSON + SVG diagram."""
import json
import os

# chain -> [(code_suffix, name, position, typical_partners(suffixes), fictional example)]
CHAINS = {
    'CHAIN_SMART_HW': {
        'name': '智能硬件',
        'links': [
            ('CHIP', '芯片与元器件', '上游', ['MODULE', 'SENSOR'], '虚构「芯启微电子」提供低功耗蓝牙 SoC'),
            ('SENSOR', '传感器与模组', '上游', ['CHIP', 'PCB'], '虚构「感知科技」生产环境传感器模组'),
            ('PCB', 'PCB 与结构件', '上游', ['MODULE', 'OEM_HW'], '虚构「精联电路」提供 4 层板打样'),
            ('MODULE', '模组与方案集成', '中游', ['PCB', 'OEM_HW', 'FW'], '虚构「联创方案」做整机方案设计'),
            ('FW', '固件与嵌入式软件', '中游', ['MODULE', 'APP'], '虚构「启源软件」提供 RTOS 固件开发'),
            ('OEM_HW', '整机制造代工', '中游', ['MODULE', 'FW', 'CHANNEL'], '虚构「智造工厂」年产能 50 万台'),
            ('APP', '应用与云平台', '下游', ['FW', 'CHANNEL'], '虚构「云控互联」提供设备管理云'),
            ('CHANNEL', '渠道与零售', '下游', ['OEM_HW', 'APP'], '虚构「优品渠道」覆盖 200 家门店'),
        ],
    },
    'CHAIN_NEW_ENERGY': {
        'name': '新能源',
        'links': [
            ('LITHIUM', '锂矿与正负极材料', '上游', ['CELL', 'RECYCLE'], '虚构「西岭锂业」供应电池级碳酸锂'),
            ('SEPARATOR', '隔膜与电解液', '上游', ['CELL'], '虚构「膜科新材」生产陶瓷涂覆隔膜'),
            ('CELL', '电芯制造', '中游', ['LITHIUM', 'SEPARATOR', 'PACK'], '虚构「恒芯动力」量产磷酸铁锂电芯'),
            ('PACK', '电池 pack 与 BMS', '中游', ['CELL', 'EPC'], '虚构「聚能 pack」做储能电池成组'),
            ('EPC', '储能系统集成 EPC', '中游', ['PACK', 'OPS'], '虚构「储建工程」承接工商业储能 EPC'),
            ('OPS', '电站运维与能源管理', '下游', ['EPC', 'RECYCLE'], '虚构「运维通」管理 300MWh 电站'),
            ('RECYCLE', '回收与梯次利用', '下游', ['PACK', 'LITHIUM'], '虚构「循环新材」年处理 2 万吨退役电池'),
        ],
    },
    'CHAIN_BIOPHARMA': {
        'name': '生物医药',
        'links': [
            ('CRO', '药物发现 CRO', '上游', ['API', 'CLINICAL'], '虚构「先导医药」提供靶点筛选服务'),
            ('API', '原料药与中间体', '上游', ['FORMULATION'], '虚构「合成制药」生产特色原料药'),
            ('FORMULATION', '制剂研发与生产', '中游', ['API', 'CLINICAL', 'DISTRIBUTION'], '虚构「制剂中心」做缓释片剂 CDMO'),
            ('CLINICAL', '临床试验与注册', '中游', ['CRO', 'FORMULATION'], '虚构「临床通」承接 II 期临床'),
            ('DISTRIBUTION', '医药流通与配送', '下游', ['FORMULATION', 'RETAIL_PHARM'], '虚构「康链医药」覆盖 800 家医院'),
            ('RETAIL_PHARM', '零售药房与 DTP', '下游', ['DISTRIBUTION', 'MED_DEVICE'], '虚构「惠民药房」DTP 药房 40 家'),
            ('MED_DEVICE', '医疗器械与诊断', '下游', ['RETAIL_PHARM', 'CLINICAL'], '虚构「诊准器械」做 POCT 检测'),
        ],
    },
    'CHAIN_ENT_SW': {
        'name': '企业软件',
        'links': [
            ('IaaS', '云基础设施', '上游', ['PaaS', 'SECURITY'], '虚构「云基科技」提供区域云资源'),
            ('SECURITY', '安全与合规服务', '上游', ['PaaS', 'SaaS_APP'], '虚构「安盾」做等保测评与审计'),
            ('PaaS', 'aPaaS 与中间件', '中游', ['IaaS', 'SaaS_APP'], '虚构「搭搭云」提供低代码平台'),
            ('SaaS_APP', '行业 SaaS 应用', '中游', ['PaaS', 'SI', 'OPS_SW'], '虚构「店管通」做零售门店 SaaS'),
            ('SI', '系统集成与实施', '中游', ['SaaS_APP', 'OPS_SW'], '虚构「联合实施」做 ERP 落地'),
            ('OPS_SW', '运维托管与 MSP', '下游', ['SI', 'SaaS_APP'], '虚构「运维家」提供 7×24 托管'),
            ('DATA_SVC', '数据服务与咨询', '下游', ['SaaS_APP', 'SI'], '虚构「数策咨询」做经营分析'),
        ],
    },
    'CHAIN_CONSUMER': {
        'name': '消费品牌',
        'links': [
            ('RAW_MAT', '原料与代工', '上游', ['BRAND', 'PACKAGE'], '虚构「源味食品」做冻干原料代工'),
            ('PACKAGE', '包装与设计', '上游', ['BRAND'], '虚构「印美包装」做环保包装设计'),
            ('BRAND', '品牌与产品研发', '中游', ['RAW_MAT', 'PACKAGE', 'ECOM', 'DIST'], '虚构「轻食日记」新锐健康零食品牌'),
            ('ECOM', '电商运营与直播', '下游', ['BRAND', 'LOGISTICS'], '虚构「流量工场」做店播代运营'),
            ('DIST', '经销与零售网络', '下游', ['BRAND', 'LOGISTICS'], '虚构「全域经销」覆盖 3000 个终端'),
            ('LOGISTICS', '仓配与履约', '下游', ['ECOM', 'DIST'], '虚构「速仓」做前置仓履约'),
            ('MKT', '营销与内容服务', '下游', ['BRAND', 'ECOM'], '虚构「种草社」做内容营销'),
        ],
    },
}

PRODUCT = 'PROD_'


def code(chain, suf):
    return f'{chain.replace("CHAIN_", "CH_")}_{suf}'


rows = []
for chain, data in CHAINS.items():
    for suf, name, pos, partners, example in data['links']:
        rows.append([
            code(chain, suf), name, data['name'], pos,
            '、'.join(code(chain, p) for p in partners),
            example,
        ])

content = {'sheets': [
    {
        'title': '产业链环节字典',
        'section': '一、产业链环节标签字典（5 条产业链，每条 6–8 个环节，共 36 个）',
        'headers': ['编码', '环节名称', '所属产业链', '上下游位置', '典型合作对象（引用编码）', '虚构企业示例'],
        'widths': [30, 22, 14, 12, 46, 44],
        'rows': rows,
    },
    {
        'title': '上下游关系图',
        'section': '二、上下游关系图（SVG 见同目录 chain-map.svg；每链按 上游→中游→下游 分层）',
        'headers': ['产业链', '上游环节', '中游环节', '下游环节'],
        'widths': [16, 34, 34, 34],
        'rows': [
            [d['name'],
             '、'.join(n for s, n, p, _, _ in d['links'] if p == '上游'),
             '、'.join(n for s, n, p, _, _ in d['links'] if p == '中游'),
             '、'.join(n for s, n, p, _, _ in d['links'] if p == '下游')]
            for d in CHAINS.values()
        ],
    },
]}

json.dump(content, open('content.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# flat JSON deliverable
out = []
for chain, data in CHAINS.items():
    for suf, name, pos, partners, example in data['links']:
        out.append({
            '编码': code(chain, suf),
            '环节名称': name,
            '所属产业链': data['name'],
            '上下游位置': pos,
            '典型合作对象': [code(chain, p) for p in partners],
            '虚构企业示例': example,
        })
json.dump(out, open('产业链环节字典.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

codes = {o['编码'] for o in out}
bad = [(o['编码'], p) for o in out for p in o['典型合作对象'] if p not in codes]
assert not bad, bad
per_chain = {}
for o in out:
    per_chain.setdefault(o['所属产业链'], 0)
    per_chain[o['所属产业链']] += 1
assert all(v >= 6 for v in per_chain.values()), per_chain
print('links:', len(out), '| per chain:', per_chain, '| dangling partners:', len(bad))


# ---------- SVG diagram ----------
def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


COL_W = 260
COL_GAP = 60
ROW_H = 68
LANE = ['上游', '中游', '下游']
HEAD_H = 96
W = COL_W * 3 + COL_GAP * 2 + 80
H = HEAD_H + sum(max(1, len([1 for s, n, p, _, _ in d['links'] if p == lane])) for d in CHAINS.values() for lane in ['上游']) * ROW_H + 80

# compute per-chain block height
heights = []
for chain, d in CHAINS.items():
    m = max(len([1 for s, n, p, _, _ in d['links'] if p == lane]) for lane in LANE)
    heights.append(m * ROW_H + 46)
H = HEAD_H + sum(heights) + 40

parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Microsoft YaHei, sans-serif">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="{W/2}" y="42" text-anchor="middle" font-size="22" font-weight="bold">产业链环节上下游关系图（5 条产业链 · 36 个环节 · 虚构示例）</text>',
         f'<text x="{W/2}" y="68" text-anchor="middle" font-size="13" fill="#666">上游 → 中游 → 下游；方框内为环节名称，箭头为上下游衔接关系</text>']

y = HEAD_H
for idx, (chain, d) in enumerate(CHAINS.items()):
    block_h = heights[idx]
    parts.append(f'<text x="24" y="{y + 16}" font-size="15" font-weight="bold" fill="#1a4d80">{esc(d["name"])}</text>')
    lanes = {lane: [n for s, n, p, _, _ in d['links'] if p == lane] for lane in LANE}
    for li, lane in enumerate(LANE):
        cx = 40 + li * (COL_W + COL_GAP)
        parts.append(f'<text x="{cx + COL_W/2}" y="{y + 38}" text-anchor="middle" font-size="11" fill="#888">{lane}</text>')
        for ri, name in enumerate(lanes[lane]):
            by = y + 46 + ri * ROW_H
            parts.append(f'<rect x="{cx}" y="{by}" width="{COL_W}" height="40" rx="6" fill="#eef4fa" stroke="#4a7fb5" stroke-width="1.2"/>')
            parts.append(f'<text x="{cx + COL_W/2}" y="{by + 25}" text-anchor="middle" font-size="12.5" fill="#123">{esc(name)}</text>')
            if li < 2:
                ay = by + 20
                parts.append(f'<line x1="{cx + COL_W}" y1="{ay}" x2="{cx + COL_W + COL_GAP}" y2="{ay}" stroke="#8fb4d8" stroke-width="1.4" marker-end="url(#ar)"/>')
    y += block_h

parts.insert(1, '<defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#8fb4d8"/></marker></defs>')
parts.append('</svg>')
svg = '\n'.join(parts)
open('chain-map.svg', 'w', encoding='utf-8').write(svg)
print('svg written:', len(svg), 'bytes')
