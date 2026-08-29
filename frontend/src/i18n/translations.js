export const translations = {
  en: {
    nav: {
      home: 'Home',
      analyze: 'Analyze Fish',
      history: 'History',
      guide: 'Freshness Guide',
      howItWorks: 'How It Works',
      about: 'About Research',
      dashboard: 'Dashboard',
      admin: 'Admin Portal',
      login: 'Login',
      register: 'Sign Up',
      logout: 'Logout'
    },
    home: {
      tag: 'AI-Assisted Fish Freshness Visual Assessment (2026)',
      title: 'Real-Time Fish Freshness Classification for Wet Markets',
      subtitle: 'Trained on local wet market fish specimens in Roxas, Oriental Mindoro. Capture or upload a photo for instant visual freshness analysis using Convolutional Neural Networks.',
      btnAnalyze: 'Analyze Fish Now',
      btnLearn: 'How It Works',
      btnGuide: 'View Freshness Guide',
      researchTitle: 'Research Domain: Roxas, Oriental Mindoro',
      researchDesc: 'Developed to empower local fish vendors, market buyers, and food researchers with objective, image-based freshness assessments.',
      disclaimerShort: 'AI-assisted visual assessment only. Not a laboratory safety test.'
    },
    analyze: {
      title: 'Analyze Fish Freshness',
      subtitle: 'Position the fish clearly inside the camera frame or upload an image.',
      tabCamera: 'Live Camera Capture',
      tabUpload: 'Upload Fish Image',
      btnCapture: 'Take Photo',
      btnRetake: 'Retake Photo',
      btnAnalyze: 'Run CNN Analysis',
      btnCancel: 'Clear',
      dropzoneText: 'Drag and drop fish photo here, or click to browse',
      dropzoneSub: 'Supports JPG, PNG, WEBP (Max 10MB)',
      analyzingText: 'Analyzing Fish Specimen...',
      analyzingStep1: 'Evaluating image clarity, lighting & sharpness...',
      analyzingStep2: 'Extracting anatomical features (eyes, gills, skin)...',
      analyzingStep3: 'Computing MobileNetV2 CNN class probabilities...',
      analyzingStep4: 'Synthesizing visual indicators & recommendations...'
    },
    result: {
      title: 'Freshness Assessment Result',
      confidence: 'AI Confidence',
      indicatorsTitle: 'Detected Visible Indicators',
      recommendationTitle: 'Culinary & Handling Recommendation',
      qualityTitle: 'Image Quality Diagnostics',
      disclaimerTitle: 'Important Food Safety Notice',
      btnAnalyzeAnother: 'Analyze Another Fish',
      btnViewHistory: 'View Scan History',
      btnPrint: 'Print Assessment'
    },
    categories: {
      fresh: 'Fresh',
      moderately_fresh: 'Moderately Fresh',
      less_fresh: 'Not Fresh',
      not_fresh: 'Spoiled'
    }
  },
  tl: {
    nav: {
      home: 'Tahanan',
      analyze: 'Suriin ang Isda',
      history: 'Kasaysayan',
      guide: 'Gabay sa Kasariwaan',
      howItWorks: 'Paano Gumagana',
      about: 'Tungkol sa Pananaliksik',
      dashboard: 'Dashboard',
      admin: 'Admin Portal',
      login: 'Mag-login',
      register: 'Magrehistro',
      logout: 'Mag-logout'
    },
    home: {
      tag: 'AI-Assisted na Pagsusuri ng Kasariwaan ng Isda (2026)',
      title: 'Mabilisang Pag-uuri ng Kasariwaan ng Isda sa Palengke',
      subtitle: 'Sinasanay sa mga isda sa lokal na pamilihan ng Roxas, Oriental Mindoro. Kumuha o mag-upload ng larawan para sa agarang visual analysis gamit ang Convolutional Neural Network (CNN).',
      btnAnalyze: 'Suriin ang Isda Ngayon',
      btnLearn: 'Paano Ito Gumagana',
      btnGuide: 'Tingnan ang Gabay',
      researchTitle: 'Lokal na Pamilihan: Roxas, Oriental Mindoro',
      researchDesc: 'Binuo upang tulungan ang mga tindero, mamimili, at mananaliksik sa pamamagitan ng visual AI analysis ng isda.',
      disclaimerShort: 'AI-assisted visual assessment lamang. Hindi laboratory test.'
    },
    analyze: {
      title: 'Suriin ang Kasariwaan ng Isda',
      subtitle: 'Itapat nang maayos ang isda sa loob ng kamera o mag-upload ng larawan.',
      tabCamera: 'Kumuha gamit ang Kamera',
      tabUpload: 'Mag-upload ng Larawan',
      btnCapture: 'Kumuha ng Litrato',
      btnRetake: 'Kumuha Muli',
      btnAnalyze: 'Simulan ang Pagsusuri',
      btnCancel: 'Alisin',
      dropzoneText: 'I-drag ang litrato ng isda rito, o pindutin para pumili',
      dropzoneSub: 'Tumatanggap ng JPG, PNG, WEBP (Hanggang 10MB)',
      analyzingText: 'Sinusuri ang Larawan ng Isda...',
      analyzingStep1: 'Sinusuri ang linaw, liwanag, at pokus ng larawan...',
      analyzingStep2: 'Kinukuha ang katangian ng mata, hasang, at kaliskis...',
      analyzingStep3: 'Kinakalkula ang MobileNetV2 CNN probabilities...',
      analyzingStep4: 'Binubuo ang rekomendasyon at mga palatandaan...'
    },
    result: {
      title: 'Resulta ng Pagsusuri',
      confidence: 'Antas ng Tiwala ng AI',
      indicatorsTitle: 'Mga Nakitang Pisikal na Palatandaan',
      recommendationTitle: 'Rekomendasyon sa Pagluluto at Pag-imbak',
      qualityTitle: 'Suri sa Kalidad ng Larawan',
      disclaimerTitle: 'Mahalagang Paalala sa Kaligtasan',
      btnAnalyzeAnother: 'Suriin ang Ibang Isda',
      btnViewHistory: 'Tingnan ang Kasaysayan',
      btnPrint: 'I-print ang Resulta'
    },
    categories: {
      fresh: 'Sariwa',
      moderately_fresh: 'Katamtamang Sariwa',
      less_fresh: 'Hindi Na Sariwa',
      not_fresh: 'Bilasa'
    }
  }
};
