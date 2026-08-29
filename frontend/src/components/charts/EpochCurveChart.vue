<template>
  <div class="epoch-chart-card">
    <div class="chart-header">
      <h4>Training & Validation Curves</h4>
      <div class="chart-toggles">
        <button 
          class="toggle-btn" 
          :class="{ active: activeMetric === 'accuracy' }"
          @click="activeMetric = 'accuracy'"
        >
          Accuracy
        </button>
        <button 
          class="toggle-btn" 
          :class="{ active: activeMetric === 'loss' }"
          @click="activeMetric = 'loss'"
        >
          Loss
        </button>
      </div>
    </div>

    <!-- Canvas Visualization -->
    <div class="canvas-container">
      <canvas ref="chartCanvas" width="500" height="240"></canvas>
    </div>

    <!-- Legend -->
    <div class="chart-legend">
      <span class="legend-item">
        <span class="legend-line train-line"></span> Training {{ activeMetric === 'accuracy' ? 'Accuracy' : 'Loss' }}
      </span>
      <span class="legend-item">
        <span class="legend-line val-line"></span> Validation {{ activeMetric === 'accuracy' ? 'Accuracy' : 'Loss' }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';

const props = defineProps({
  history: {
    type: Object,
    default: () => ({
      train_accuracy_curve: [0.45, 0.62, 0.74, 0.81, 0.88, 0.92, 0.96, 0.98, 1.0],
      val_accuracy_curve: [0.40, 0.55, 0.65, 0.71, 0.73, 0.74, 0.75, 0.75, 0.75],
      train_loss_curve: [1.45, 1.10, 0.82, 0.55, 0.38, 0.22, 0.12, 0.05, 0.01],
      val_loss_curve: [1.50, 1.25, 0.98, 0.82, 0.75, 0.72, 0.71, 0.70, 0.70]
    })
  }
});

const activeMetric = ref('accuracy');
const chartCanvas = ref(null);

function renderChart() {
  const canvas = chartCanvas.value;
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;
  const padding = 35;

  ctx.clearRect(0, 0, w, h);

  const trainData = activeMetric.value === 'accuracy' 
    ? (props.history.train_accuracy_curve || [0.5, 0.7, 0.9, 1.0])
    : (props.history.train_loss_curve || [1.5, 1.0, 0.5, 0.1]);

  const valData = activeMetric.value === 'accuracy'
    ? (props.history.val_accuracy_curve || [0.4, 0.6, 0.7, 0.75])
    : (props.history.val_loss_curve || [1.6, 1.2, 0.8, 0.7]);

  const maxVal = activeMetric.value === 'accuracy' ? 1.0 : Math.max(...trainData, ...valData, 1.5);
  const minVal = 0;

  // Grid Lines
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
  ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const y = padding + (h - 2 * padding) * (i / 4);
    ctx.beginPath();
    ctx.moveTo(padding, y);
    ctx.lineTo(w - padding, y);
    ctx.stroke();

    // Y Axis Labels
    ctx.fillStyle = '#64748b';
    ctx.font = '10px Plus Jakarta Sans';
    const labelVal = (maxVal - (maxVal - minVal) * (i / 4)).toFixed(1);
    ctx.fillText(labelVal, 5, y + 3);
  }

  function drawLine(data, color, isDashed = false) {
    if (!data || data.length < 2) return;
    ctx.strokeStyle = color;
    ctx.lineWidth = 2.5;
    if (isDashed) ctx.setLineDash([4, 4]);
    else ctx.setLineDash([]);

    ctx.beginPath();
    for (let i = 0; i < data.length; i++) {
      const x = padding + (w - 2 * padding) * (i / (data.length - 1));
      const normalized = (data[i] - minVal) / (maxVal - minVal);
      const y = h - padding - normalized * (h - 2 * padding);

      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();

    // Data points
    ctx.fillStyle = color;
    for (let i = 0; i < data.length; i++) {
      const x = padding + (w - 2 * padding) * (i / (data.length - 1));
      const normalized = (data[i] - minVal) / (maxVal - minVal);
      const y = h - padding - normalized * (h - 2 * padding);
      ctx.beginPath();
      ctx.arc(x, y, 3.5, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  // Draw Curves
  drawLine(trainData, '#0ea5e9', false);
  drawLine(valData, '#14b8a6', true);
}

onMounted(() => {
  renderChart();
});

watch([activeMetric, () => props.history], () => {
  renderChart();
}, { deep: true });
</script>

<style scoped>
.epoch-chart-card {
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-md);
  padding: 1.5rem;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.chart-toggles {
  display: flex;
  gap: 0.35rem;
  background: rgba(0, 0, 0, 0.3);
  padding: 0.2rem;
  border-radius: var(--radius-sm);
}

.toggle-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.6rem;
  border-radius: 4px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.toggle-btn.active {
  background: var(--primary);
  color: #fff;
}

.canvas-container {
  width: 100%;
  overflow-x: auto;
}

canvas {
  width: 100%;
  height: auto;
  display: block;
}

.chart-legend {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-top: 0.85rem;
  font-size: 0.8rem;
  color: var(--text-muted);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.legend-line {
  width: 18px;
  height: 3px;
  border-radius: 2px;
}

.train-line { background: #0ea5e9; }
.val-line { background: #14b8a6; border-bottom: 1px dashed #14b8a6; }
</style>
