const Database = require('better-sqlite3');
const path = require('path');
const fs = require('fs');
const bcrypt = require('bcryptjs');

const dbPath = path.resolve(__dirname, '../../freshcatch.db');
const db = new Database(dbPath);

// Enable WAL mode for optimal concurrent performance
db.pragma('journal_mode = WAL');

function initializeDatabase() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      email TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL,
      role TEXT NOT NULL CHECK(role IN ('consumer', 'vendor', 'admin', 'researcher')) DEFAULT 'consumer',
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS fish_species (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL UNIQUE,
      local_name TEXT NOT NULL,
      scientific_name TEXT,
      description TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS freshness_categories (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      code TEXT UNIQUE NOT NULL,
      name TEXT NOT NULL,
      tagalog_name TEXT NOT NULL,
      description TEXT NOT NULL,
      visual_characteristics TEXT,
      recommendation TEXT NOT NULL,
      recommendation_tagalog TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS predictions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
      species_id INTEGER REFERENCES fish_species(id) ON DELETE SET NULL,
      image_url TEXT NOT NULL,
      classification TEXT NOT NULL,
      confidence REAL NOT NULL,
      class_probabilities TEXT NOT NULL,
      visual_indicators TEXT NOT NULL,
      recommendation TEXT NOT NULL,
      recommendation_tagalog TEXT,
      quality_metrics TEXT,
      model_version TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS dataset_images (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      filename TEXT NOT NULL,
      image_url TEXT NOT NULL,
      species_id INTEGER REFERENCES fish_species(id),
      freshness_category_id INTEGER REFERENCES freshness_categories(id),
      split TEXT CHECK(split IN ('train', 'validation', 'test')) DEFAULT 'train',
      lighting_condition TEXT,
      background_condition TEXT,
      fish_orientation TEXT,
      distance_condition TEXT,
      image_quality TEXT,
      source TEXT,
      capture_date TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS models (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      model_name TEXT NOT NULL,
      version TEXT UNIQUE NOT NULL,
      architecture TEXT NOT NULL,
      accuracy REAL NOT NULL,
      precision REAL NOT NULL,
      recall REAL NOT NULL,
      f1_score REAL NOT NULL,
      confusion_matrix TEXT,
      classification_report TEXT,
      file_path TEXT NOT NULL,
      status TEXT CHECK(status IN ('active', 'archived', 'evaluating')) DEFAULT 'evaluating',
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS environmental_evaluations (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      model_id INTEGER REFERENCES models(id),
      condition_type TEXT NOT NULL,
      condition_value TEXT NOT NULL,
      accuracy REAL NOT NULL,
      f1_score REAL NOT NULL,
      sample_count INTEGER NOT NULL,
      notes TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS error_analysis_logs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      model_id INTEGER REFERENCES models(id),
      image_url TEXT NOT NULL,
      actual_class TEXT NOT NULL,
      predicted_class TEXT NOT NULL,
      confidence REAL NOT NULL,
      environmental_condition TEXT,
      error_cause TEXT,
      researcher_notes TEXT,
      reviewed_by INTEGER REFERENCES users(id),
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
  `);

  seedInitialData();
}

function seedInitialData() {
  // 1. Seed Users
  const userCount = db.prepare('SELECT COUNT(*) AS count FROM users').get().count;
  if (userCount === 0) {
    const salt = bcrypt.genSaltSync(10);
    const insertUser = db.prepare('INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)');

    insertUser.run('Elena Santos (Consumer)', 'consumer@freshcatch.ai', bcrypt.hashSync('password123', salt), 'consumer');
    insertUser.run('Mang Berting (Fish Vendor - Roxas Public Market)', 'vendor@freshcatch.ai', bcrypt.hashSync('password123', salt), 'vendor');
    insertUser.run('System Administrator', 'admin@freshcatch.ai', bcrypt.hashSync('admin123', salt), 'admin');
    insertUser.run('Dr. Aris Rodriguez (Fisheries Researcher)', 'researcher@freshcatch.ai', bcrypt.hashSync('research123', salt), 'researcher');
    console.log('Default users seeded successfully.');
  }

  // 2. Seed Fish Species (Roxas, Oriental Mindoro)
  const speciesCount = db.prepare('SELECT COUNT(*) AS count FROM fish_species').get().count;
  if (speciesCount === 0) {
    const insertSpecies = db.prepare('INSERT INTO fish_species (name, local_name, scientific_name, description) VALUES (?, ?, ?, ?)');
    const speciesList = [
      ['Bangus (Milkfish)', 'Bangus', 'Chanos chanos', 'National fish of the Philippines, abundant in Roxas fishponds and Mindoro coastal waters.'],
      ['Tilapia', 'Tilapia', 'Oreochromis niloticus', 'Common freshwater and brackish fish widely sold across Oriental Mindoro wet markets.'],
      ['Galunggong (Round Scad)', 'Galunggong', 'Decapterus punctatus', 'Staple pelagic fish harvested from Tablas Strait and Mindoro waters.'],
      ['Tamban (Sardines)', 'Tamban', 'Sardinella lemuru', 'Small oily fish common in Mindoro coastal fisheries.'],
      ['Matangbaka (Bigeye Scad)', 'Matangbaka', 'Selar crumenophthalmus', 'Characterized by distinctively large eyes, popular in Roxas seafood markets.'],
      ['Tulingan (Mackerel Tuna)', 'Tulingan', 'Auxis thazard', 'Oceanic tuna species frequently prepared in sinaing na tulingan.'],
      ['Maya-Maya (Red Snapper)', 'Maya-Maya', 'Lutjanus campechanus', 'Prized reef fish with distinct reddish hue.'],
      ['Tanigue (Spanish Mackerel)', 'Tanigue', 'Scomberomorus commerson', 'High-value predator fish with firm white flesh, ideal for kinilaw.']
    ];

    for (const sp of speciesList) {
      insertSpecies.run(...sp);
    }
    console.log('Fish species seeded.');
  }

  // 3. Seed Freshness Categories
  const catCount = db.prepare('SELECT COUNT(*) AS count FROM freshness_categories').get().count;
  if (catCount === 0) {
    const insertCat = db.prepare(`
      INSERT INTO freshness_categories 
      (code, name, tagalog_name, description, visual_characteristics, recommendation, recommendation_tagalog) 
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `);

    insertCat.run(
      'fresh',
      'Fresh',
      'Sariwa',
      'Fish in prime visual condition, showing convex transparent eyes, bright red/pink gills, and firm shimmering scales.',
      JSON.stringify(['Clear prominent convex eyes with black pupil', 'Vibrant ruby red/pink opercular gill coloration', 'High metallic iridescent sheen on intact scales', 'Firm, elastic body contour']),
      'The fish appears visually fresh based on the trained model. Highly suitable for raw preparation (kinilaw), sinigang, grilling, and steaming.',
      'Ang isda ay mukhang sariwa ayon sa AI model. Angkop na angkop sa kinilaw, sinigang, inihaw, o pasingaw.'
    );

    insertCat.run(
      'moderately_fresh',
      'Moderately Fresh',
      'Katamtamang Sariwa',
      'Fish exhibiting acceptable freshness with slight cornea flattening and mild reduction in scale luster.',
      JSON.stringify(['Slightly flattened eye cornea with minor haze', 'Dull red or pinkish-brown gill margins', 'Moderate scale luster with slight color fading', 'Firm body texture']),
      'The fish exhibits moderate freshness. Recommended for prompt cooking methods such as frying, paksiw, escabeche, or sarciado.',
      'Katamtamang sariwa ang isda. Mainam lutuin agad gaya ng prito, paksiw, o escabeche.'
    );

    insertCat.run(
      'less_fresh',
      'Less Fresh',
      'Hindi Gaanong Sariwa',
      'Fish showing noticeable freshness deterioration, sunken cloudy eyes, and bleached or brownish gills.',
      JSON.stringify(['Sunken cloudy or opaque eyes', 'Pale brownish or bleached gills', 'Dull discolored skin with loose scales', 'Softening flesh tissue']),
      'The fish shows signs of deteriorating freshness. Requires thorough cooking with generous spices. Inspect smell and texture before purchase.',
      'Hindi gaanong sariwa ang isda. Nangangailangan ng masusing pagluluto at pampalasa; amuyin at suriin bago bilhin.'
    );

    insertCat.run(
      'not_fresh',
      'Not Fresh',
      'Bilasa',
      'Fish with marked visual signs of staleness and decomposition. Heavily sunken eyes, dark slimy gills, and loose discolored skin.',
      JSON.stringify(['Deeply sunken, opaque milky-grey cornea', 'Dark brown or grey slimy gills', 'Marked skin discoloration, wrinkling, or mucus', 'Flaccid, mushy belly tissue']),
      'The fish appears stale or spoiled. Not recommended for purchase or consumption due to potential food safety hazards.',
      'Mukhang bilasa ang isda. Hindi inirerekomendang bilhin o kainin dahil sa panganib ng pagkapanis.'
    );
    console.log('Freshness categories seeded.');
  }

  // 4. Seed Active Model & Evaluation Results if available
  const modelCount = db.prepare('SELECT COUNT(*) AS count FROM models').get().count;
  const evalPath = path.resolve(__dirname, '../../../ai/models/saved/evaluation_results.json');
  if (modelCount === 0 && fs.existsSync(evalPath)) {
    try {
      const evalData = JSON.parse(fs.readFileSync(evalPath, 'utf8'));
      const insertModel = db.prepare(`
        INSERT INTO models 
        (model_name, version, architecture, accuracy, precision, recall, f1_score, confusion_matrix, classification_report, file_path, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `);

      insertModel.run(
        'FreshCatch MobileNetV2 Classifier',
        evalData.model_version || 'FreshCatch-CNN-v1.0-MobileNetV2',
        'MobileNetV2 Transfer Learning + Dense Head',
        evalData.metrics.accuracy,
        evalData.metrics.precision_macro,
        evalData.metrics.recall_macro,
        evalData.metrics.f1_score_macro,
        JSON.stringify(evalData.confusion_matrix),
        JSON.stringify(evalData.per_class_metrics),
        'ai/models/saved/freshcatch_cnn_v1.joblib',
        'active'
      );
      console.log('Active model record seeded with evaluated metrics.');
    } catch (err) {
      console.error('Error seeding active model record:', err.message);
    }
  }

  // 5. Seed Dataset Images from ai/dataset/metadata.json
  const datasetCount = db.prepare('SELECT COUNT(*) AS count FROM dataset_images').get().count;
  const metadataPath = path.resolve(__dirname, '../../../ai/dataset/metadata.json');
  if (datasetCount === 0 && fs.existsSync(metadataPath)) {
    try {
      const metaRecords = JSON.parse(fs.readFileSync(metadataPath, 'utf8'));
      const speciesMap = {};
      db.prepare('SELECT id, name, local_name FROM fish_species').all().forEach(s => {
        speciesMap[s.name] = s.id;
        speciesMap[s.local_name] = s.id;
      });

      const catMap = {};
      db.prepare('SELECT id, name, code FROM freshness_categories').all().forEach(c => {
        catMap[c.name] = c.id;
        catMap[c.code] = c.id;
      });

      const insertDataset = db.prepare(`
        INSERT INTO dataset_images 
        (filename, image_url, species_id, freshness_category_id, split, lighting_condition, background_condition, fish_orientation, distance_condition, image_quality, source, capture_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `);

      const insertMany = db.transaction((records) => {
        for (const r of records) {
          const sId = speciesMap[r.species_name] || speciesMap[r.species_local_name] || 1;
          const cId = catMap[r.freshness_category] || catMap[r.freshness_code] || 1;
          insertDataset.run(
            r.filename,
            r.image_url,
            sId,
            cId,
            r.split || 'train',
            r.lighting_condition || 'Normal',
            r.background_condition || 'Wet-market',
            r.fish_orientation || 'Side',
            r.distance_condition || 'Medium',
            r.image_quality || 'High',
            r.source || 'Roxas Public Market, Oriental Mindoro',
            r.capture_date || '2026-08-19'
          );
        }
      });

      insertMany(metaRecords);
      console.log(`Synced ${metaRecords.length} dataset images into database.`);
    } catch (err) {
      console.error('Error syncing dataset metadata:', err.message);
    }
  }

  // 6. Seed Sample Predictions for demo history
  const predCount = db.prepare('SELECT COUNT(*) AS count FROM predictions').get().count;
  if (predCount === 0) {
    const insertPred = db.prepare(`
      INSERT INTO predictions 
      (user_id, species_id, image_url, classification, confidence, class_probabilities, visual_indicators, recommendation, recommendation_tagalog, quality_metrics, model_version, created_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);

    insertPred.run(
      1, 1, '/dataset/raw/fish_0001_bangus_fresh_bright.jpg', 'Fresh', 0.924,
      JSON.stringify({ 'Fresh': 0.924, 'Moderately Fresh': 0.052, 'Less Fresh': 0.016, 'Not Fresh': 0.008 }),
      JSON.stringify([
        { region: 'Eyes', label: 'Clear, convex cornea with distinct pupil', status: 'fresh' },
        { region: 'Gills', label: 'Vibrant red / pink opercular coloration', status: 'fresh' },
        { region: 'Skin & Scales', label: 'Natural metallic sheen and intact tight scales', status: 'fresh' }
      ]),
      'The fish appears visually fresh based on the trained model. Highly suitable for raw preparation (kinilaw), sinigang, grilling, and steaming.',
      'Ang isda ay mukhang sariwa ayon sa AI model. Angkop na angkop sa kinilaw, sinigang, inihaw, o pasingaw.',
      JSON.stringify({ blur_variance: 142.5, brightness_mean: 184.2, contrast_std: 42.1 }),
      'FreshCatch-CNN-v1.0-MobileNetV2',
      '2026-08-19 08:30:00'
    );

    insertPred.run(
      2, 2, '/dataset/raw/fish_0025_tilapia_moderately_fresh_normal.jpg', 'Moderately Fresh', 0.841,
      JSON.stringify({ 'Fresh': 0.089, 'Moderately Fresh': 0.841, 'Less Fresh': 0.051, 'Not Fresh': 0.019 }),
      JSON.stringify([
        { region: 'Eyes', label: 'Slight flattening of cornea with mild haze', status: 'moderate' },
        { region: 'Gills', label: 'Slightly dull red gill coloration', status: 'moderate' },
        { region: 'Skin & Scales', label: 'Moderate scale luster with slight color fading', status: 'moderate' }
      ]),
      'The fish exhibits moderate freshness. Recommended for prompt cooking methods such as frying, paksiw, escabeche, or sarciado.',
      'Katamtamang sariwa ang isda. Mainam lutuin agad gaya ng prito, paksiw, o escabeche.',
      JSON.stringify({ blur_variance: 98.4, brightness_mean: 145.0, contrast_std: 38.6 }),
      'FreshCatch-CNN-v1.0-MobileNetV2',
      '2026-08-18 14:15:00'
    );
  }
}

initializeDatabase();

module.exports = db;
