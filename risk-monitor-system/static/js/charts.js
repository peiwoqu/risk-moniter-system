/**
 * Agent智能风险监控管理系统 - 图表渲染 (稳健版)
 */

const CHART_COLORS = {
    critical: '#DC3545', high: '#FD7E14', medium: '#FFC107', low: '#28A745',
    primary: '#4472C4', secondary: '#6C757D',
};

// ==================== 风险矩阵热力图 ====================
function renderRiskMatrixChart(risks) {
    const canvas = document.getElementById('riskMatrixChart');
    if (!canvas) { console.log('riskMatrixChart canvas not found'); return; }
    if (!risks || !risks.length) { console.log('No risks data'); return; }

    const ctx = canvas.getContext('2d');
    const W = canvas.parentElement.clientWidth || 700;
    const H = 400;
    canvas.width = W; canvas.height = H;

    const margin = { top: 40, right: 30, bottom: 60, left: 80 };
    const gw = (W - margin.left - margin.right) / 5;
    const gh = (H - margin.top - margin.bottom) / 5;

    // Clear
    ctx.clearRect(0, 0, W, H);

    // Build a simple score grid: which cells have risks
    const grid = Array.from({length:5}, () => Array.from({length:5}, () => []));
    risks.forEach(r => {
        const p = (r.probability || 3) - 1;
        const imp = (r.impact || 3) - 1;
        if (p>=0 && p<5 && imp>=0 && imp<5) {
            grid[4-imp][p].push(r);
        }
    });

    // Draw cells
    for (let row = 0; row < 5; row++) {
        for (let col = 0; col < 5; col++) {
            const x = margin.left + col * gw;
            const y = margin.top + row * gh;
            const score = (col+1) * (5-row);

            // Background color
            if (score >= 15) ctx.fillStyle = '#ffc7ce';
            else if (score >= 10) ctx.fillStyle = '#ffd9b3';
            else if (score >= 5) ctx.fillStyle = '#ffffcc';
            else ctx.fillStyle = '#c6efce';

            ctx.fillRect(x+2, y+2, gw-4, gh-4);
            ctx.strokeStyle = '#ddd';
            ctx.lineWidth = 1;
            ctx.strokeRect(x+2, y+2, gw-4, gh-4);

            // Score label
            ctx.fillStyle = '#999';
            ctx.font = '11px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText('×'+score, x+gw/2, y+gh/2-5);

            // Risk codes
            const cell = grid[row][col];
            if (cell && cell.length > 0) {
                ctx.fillStyle = '#333';
                ctx.font = 'bold 10px sans-serif';
                ctx.fillText(cell.map(r=>r.risk_code).join(','), x+gw/2, y+gh/2+12);
            }
        }
    }

    // Y axis labels (Impact)
    const yLabels = ['极大(5)','大(4)','中等(3)','小(2)','极小(1)'];
    ctx.fillStyle = '#333';
    ctx.font = '12px sans-serif';
    ctx.textAlign = 'right';
    for (let i=0; i<5; i++) {
        const y = margin.top + i*gh + gh/2 + 4;
        ctx.fillText(yLabels[i], margin.left-10, y);
    }
    ctx.save();
    ctx.translate(15, margin.top + 2.5*gh);
    ctx.rotate(-Math.PI/2);
    ctx.textAlign = 'center';
    ctx.font = 'bold 13px sans-serif';
    ctx.fillText('影响程度 (Impact)', 0, 0);
    ctx.restore();

    // X axis labels (Probability)
    const xLabels = ['极低(1)','低(2)','中等(3)','高(4)','极高(5)'];
    ctx.textAlign = 'center';
    for (let i=0; i<5; i++) {
        const x = margin.left + i*gw + gw/2;
        ctx.fillText(xLabels[i], x, margin.top + 5*gh + 20);
    }
    ctx.font = 'bold 13px sans-serif';
    ctx.fillText('可能性 (Probability)', margin.left + 2.5*gw, margin.top + 5*gh + 42);

    // Legend
    const lx = margin.left;
    const ly = margin.top + 5*gh + 55;
    const legend = [
        {label:'重大风险(≥15)', color:'#ffc7ce'},
        {label:'高度关注(10-14)', color:'#ffd9b3'},
        {label:'一般风险(5-9)', color:'#ffffcc'},
        {label:'低风险(<5)', color:'#c6efce'},
    ];
    legend.forEach((l,i) => {
        const lox = lx + i*(W-margin.left)/4;
        ctx.fillStyle = l.color;
        ctx.fillRect(lox, ly, 14, 14);
        ctx.strokeStyle = '#ccc';
        ctx.strokeRect(lox, ly, 14, 14);
        ctx.fillStyle = '#333';
        ctx.font = '10px sans-serif';
        ctx.textAlign = 'left';
        ctx.fillText(l.label, lox+18, ly+12);
    });
}

// ==================== 风险趋势图 (Doughnut) ====================
function renderTrendChart(risks) {
    const canvas = document.getElementById('trendChart');
    if (!canvas) return;
    const inc = risks.filter(r => r.trend==='increasing').length;
    const sta = risks.filter(r => r.trend==='stable').length;
    const dec = risks.filter(r => r.trend==='decreasing').length;
    new Chart(canvas, {
        type: 'doughnut',
        data: {labels:['↑上升','→稳定','↓下降'],datasets:[{data:[inc,sta,dec],backgroundColor:[CHART_COLORS.critical,CHART_COLORS.secondary,CHART_COLORS.low],borderWidth:2,borderColor:'#fff'}]},
        options: {responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'bottom'}}}
    });
}

// ==================== 风险类别分布 ====================
function renderCategoryChart(risks) {
    const canvas = document.getElementById('categoryChart');
    if (!canvas) return;
    const cats = {};
    risks.forEach(r => {
        const c = r.subcategory || r.category || '其他';
        cats[c] = (cats[c]||0)+1;
    });
    const labels = Object.keys(cats);
    new Chart(canvas, {
        type: 'bar',
        data: {labels,datasets:[{label:'风险数量',data:Object.values(cats),backgroundColor:'#4472C4',borderRadius:4}]},
        options: {indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{title:{display:true,text:'数量'},ticks:{stepSize:1}}}}
    });
}

// ==================== 风险得分分布 ====================
function renderScoreDistribution(risks) {
    const canvas = document.getElementById('scoreDistributionChart');
    if (!canvas) return;
    const bins = {'1-4':0,'5-9':0,'10-14':0,'15-19':0,'20-25':0};
    risks.forEach(r => {
        const s = r.risk_score || 0;
        if (s<=4) bins['1-4']++;
        else if (s<=9) bins['5-9']++;
        else if (s<=14) bins['10-14']++;
        else if (s<=19) bins['15-19']++;
        else bins['20-25']++;
    });
    new Chart(canvas, {
        type: 'bar',
        data: {labels:Object.keys(bins),datasets:[{label:'风险数量',data:Object.values(bins),backgroundColor:[CHART_COLORS.low,CHART_COLORS.medium,CHART_COLORS.high,CHART_COLORS.critical,'#8B0000'],borderRadius:4}]},
        options: {responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{y:{title:{display:true,text:'数量'},ticks:{stepSize:1}}}}
    });
}
