const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const PYTHON_EXECUTABLE = process.env.PYTHON_PATH || 'python';
const AI_ROOT = path.resolve(__dirname, '../../../ai');

class PythonBridgeService {
  /**
   * Runs CNN freshness inference on an image file.
   */
  static runInference(imagePath, modelPath = null) {
    return new Promise((resolve, reject) => {
      const scriptPath = path.join(AI_ROOT, 'prediction/infer.py');
      const args = [scriptPath, imagePath];
      if (modelPath) {
        args.push('--model', modelPath);
      }

      const pyProcess = spawn(PYTHON_EXECUTABLE, args, {
        cwd: path.resolve(__dirname, '../../..'),
        env: { ...process.env, PYTHONIOENCODING: 'utf-8', PYTHONUTF8: '1' },
      });

      let stdoutChunks = [];
      let stderrChunks = [];

      pyProcess.stdout.on('data', (data) => { stdoutChunks.push(data); });
      pyProcess.stderr.on('data', (data) => { stderrChunks.push(data); });

      // Use Buffer.concat + utf-8 decode to correctly handle emoji and non-ASCII chars
      const getStdout = () => Buffer.concat(stdoutChunks).toString('utf-8');
      const getStderr = () => Buffer.concat(stderrChunks).toString('utf-8');

      // Aliases so the close handler can reference them
      Object.defineProperty(pyProcess, '_getStdout', { value: getStdout });
      Object.defineProperty(pyProcess, '_getStderr', { value: getStderr });

      pyProcess.on('close', (code) => {
        const stdout = getStdout();
        const stderr = getStderr();
        if (code !== 0 && !stdout) {
          return reject(new Error(`Python inference failed (exit ${code}): ${stderr}`));
        }

        try {
          const parsed = JSON.parse(stdout.trim());
          resolve(parsed);
        } catch (err) {
          reject(new Error(`Failed to parse Python inference response: ${stdout} | Error: ${err.message}`));
        }
      });
    });
  }

  /**
   * Pre-checks image quality before classification.
   */
  static checkQuality(imagePath) {
    return new Promise((resolve, reject) => {
      const scriptPath = path.join(AI_ROOT, 'preprocessing/quality_checker.py');
      const pyProcess = spawn(PYTHON_EXECUTABLE, [scriptPath, imagePath], {
        cwd: path.resolve(__dirname, '../../..'),
        env: { ...process.env, PYTHONIOENCODING: 'utf-8', PYTHONUTF8: '1' },
      });

      const stdoutChunks = [];
      const stderrChunks = [];

      pyProcess.stdout.on('data', (data) => { stdoutChunks.push(data); });
      pyProcess.stderr.on('data', (data) => { stderrChunks.push(data); });

      pyProcess.on('close', (code) => {
        const stdout = Buffer.concat(stdoutChunks).toString('utf-8');
        const stderr = Buffer.concat(stderrChunks).toString('utf-8');
        try {
          const parsed = JSON.parse(stdout.trim());
          resolve(parsed);
        } catch (err) {
          reject(new Error(`Failed to parse quality check output: ${stdout} | ${stderr}`));
        }
      });
    });
  }

  /**
   * Triggers model training pipeline.
   */
  static triggerTraining() {
    return new Promise((resolve, reject) => {
      const scriptPath = path.join(AI_ROOT, 'training/train.py');
      const pyProcess = spawn(PYTHON_EXECUTABLE, [scriptPath], {
        cwd: path.resolve(__dirname, '../../..'),
        env: { ...process.env, PYTHONIOENCODING: 'utf-8', PYTHONUTF8: '1' },
      });

      const stdoutChunks = [];
      const stderrChunks = [];

      pyProcess.stdout.on('data', (data) => { stdoutChunks.push(data); });
      pyProcess.stderr.on('data', (data) => { stderrChunks.push(data); });

      pyProcess.on('close', (code) => {
        const stdout = Buffer.concat(stdoutChunks).toString('utf-8');
        const stderr = Buffer.concat(stderrChunks).toString('utf-8');
        if (code !== 0) {
          return reject(new Error(`Model training failed (exit ${code}): ${stderr}`));
        }
        resolve({ success: true, message: 'Training completed successfully', logs: stdout });
      });
    });
  }

  /**
   * Triggers model evaluation on test dataset.
   */
  static triggerEvaluation() {
    return new Promise((resolve, reject) => {
      const scriptPath = path.join(AI_ROOT, 'evaluation/evaluate.py');
      const pyProcess = spawn(PYTHON_EXECUTABLE, [scriptPath], {
        cwd: path.resolve(__dirname, '../../..'),
        env: { ...process.env, PYTHONIOENCODING: 'utf-8', PYTHONUTF8: '1' },
      });

      const stdoutChunks = [];
      const stderrChunks = [];

      pyProcess.stdout.on('data', (data) => { stdoutChunks.push(data); });
      pyProcess.stderr.on('data', (data) => { stderrChunks.push(data); });

      pyProcess.on('close', (code) => {
        const stdout = Buffer.concat(stdoutChunks).toString('utf-8');
        const stderr = Buffer.concat(stderrChunks).toString('utf-8');
        if (code !== 0) {
          return reject(new Error(`Model evaluation failed (exit ${code}): ${stderr}`));
        }
        resolve({ success: true, message: 'Evaluation completed successfully', logs: stdout });
      });
    });
  }

  /**
   * Retrieves verified evaluation metrics & confusion matrix from disk.
   */
  static getEvaluationResults() {
    const evalPath = path.join(AI_ROOT, 'models/saved/evaluation_results.json');
    if (fs.existsSync(evalPath)) {
      return JSON.parse(fs.readFileSync(evalPath, 'utf8'));
    }
    return null;
  }

  /**
   * Retrieves training history and epoch loss curves from disk.
   */
  static getTrainingHistory() {
    const histPath = path.join(AI_ROOT, 'models/saved/training_history.json');
    if (fs.existsSync(histPath)) {
      return JSON.parse(fs.readFileSync(histPath, 'utf8'));
    }
    return null;
  }

  /**
   * Retrieves environmental testing results from disk.
   */
  static getEnvironmentalResults() {
    const envPath = path.join(AI_ROOT, 'models/saved/environmental_results.json');
    if (fs.existsSync(envPath)) {
      return JSON.parse(fs.readFileSync(envPath, 'utf8'));
    }
    return null;
  }
}

module.exports = PythonBridgeService;
