<template>
  <div class="confusion-matrix-wrapper">
    <div class="matrix-header">
      <h4>Confusion Matrix Heatmap</h4>
      <span class="matrix-sub">Test Dataset Split (Held-out 15%)</span>
    </div>

    <div class="matrix-grid-container">
      <!-- Axis Labels -->
      <div class="axis-y-label">
        <span>ACTUAL GROUND TRUTH</span>
      </div>

      <div class="matrix-table-wrap">
        <div class="axis-x-label">
          <span>PREDICTED AI CLASSIFICATION</span>
        </div>

        <table class="matrix-table">
          <thead>
            <tr>
              <th class="corner-header">Actual \ Pred</th>
              <th v-for="cls in classes" :key="'col-' + cls" class="col-header">
                {{ cls }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(actualClass, rIdx) in classes" :key="'row-' + actualClass">
              <td class="row-header">{{ actualClass }}</td>
              <td 
                v-for="(predClass, cIdx) in classes" 
                :key="'cell-' + rIdx + '-' + cIdx"
                class="matrix-cell"
                :class="{ 'diagonal-cell': rIdx === cIdx }"
                :style="getCellStyle(matrix[rIdx] ? matrix[rIdx][cIdx] : 0, rIdx === cIdx)"
              >
                <div class="cell-content">
                  <span class="cell-val">{{ matrix[rIdx] ? matrix[rIdx][cIdx] : 0 }}</span>
                  <span v-if="matrix[rIdx] && getTotalInRow(rIdx) > 0" class="cell-pct">
                    {{ Math.round(((matrix[rIdx][cIdx] || 0) / getTotalInRow(rIdx)) * 100) }}%
                  </span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Matrix Legend -->
    <div class="matrix-legend">
      <span class="legend-item">
        <span class="legend-box diag-box"></span> Correctly Classified (Diagonal)
      </span>
      <span class="legend-item">
        <span class="legend-box error-box"></span> Misclassifications (Off-diagonal)
      </span>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  classes: {
    type: Array,
    default: () => ['Fresh', 'Moderately Fresh', 'Less Fresh', 'Not Fresh']
  },
  matrix: {
    type: Array,
    default: () => [
      [8, 0, 0, 0],
      [1, 7, 0, 0],
      [0, 1, 6, 1],
      [0, 0, 1, 8]
    ]
  }
});

function getTotalInRow(rIdx) {
  if (!props.matrix || !props.matrix[rIdx]) return 1;
  return props.matrix[rIdx].reduce((a, b) => a + b, 0);
}

function getCellStyle(val, isDiagonal) {
  if (!val || val === 0) {
    return { background: 'rgba(255, 255, 255, 0.02)', color: 'rgba(255, 255, 255, 0.25)' };
  }

  if (isDiagonal) {
    const intensity = Math.min(1, 0.25 + val * 0.1);
    return {
      background: `rgba(16, 185, 129, ${intensity})`,
      color: '#ffffff',
      fontWeight: '700'
    };
  } else {
    return {
      background: 'rgba(239, 68, 68, 0.35)',
      color: '#ffffff',
      fontWeight: '600'
    };
  }
}
</script>

<style scoped>
.confusion-matrix-wrapper {
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-md);
  padding: 1.5rem;
}

.matrix-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
}

.matrix-sub {
  font-size: 0.8rem;
  color: var(--accent-teal);
  background: rgba(20, 184, 166, 0.1);
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
}

.matrix-grid-container {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  overflow-x: auto;
}

.axis-y-label {
  writing-mode: vertical-rl;
  transform: rotate(180deg);
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--text-muted);
  letter-spacing: 0.1em;
}

.matrix-table-wrap {
  flex: 1;
}

.axis-x-label {
  text-align: center;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--text-muted);
  letter-spacing: 0.1em;
  margin-bottom: 0.5rem;
}

.matrix-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 4px;
}

.corner-header, .col-header, .row-header {
  font-size: 0.8rem;
  color: var(--text-muted);
  padding: 0.5rem;
}

.col-header {
  text-align: center;
}

.row-header {
  text-align: right;
  font-weight: 600;
  white-space: nowrap;
}

.matrix-cell {
  text-align: center;
  padding: 0.85rem 0.5rem;
  border-radius: 6px;
  min-width: 65px;
  transition: transform var(--transition-fast);
}

.matrix-cell:hover {
  transform: scale(1.04);
}

.cell-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.cell-val {
  font-size: 1.1rem;
}

.cell-pct {
  font-size: 0.7rem;
  opacity: 0.8;
}

.matrix-legend {
  display: flex;
  gap: 1.5rem;
  justify-content: center;
  margin-top: 1.25rem;
  font-size: 0.82rem;
  color: var(--text-muted);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.45rem;
}

.legend-box {
  width: 14px;
  height: 14px;
  border-radius: 3px;
}

.diag-box {
  background: rgba(16, 185, 129, 0.75);
}

.error-box {
  background: rgba(239, 68, 68, 0.6);
}
</style>
