// Preset configurations for different use cases
const PRESETS = {
  // Photo preset - optimized for photographic content
  photo: {
    outputWidth: 120,
    colorMode: 'ansi',
    dithering: true,
    edgeDetect: false,
    preset: 'photo',
    enhanceContrast: true,
    aspectRatioCorrection: 0.55,
    invert: false,
    edgeThreshold: 75,
    blur: 0,
    sharpen: 2.5,
    brightness: 1.15,
    saturation: 1.2,
    contrast: 1.3,
    detailLevel: 1.2,
    gamma: 1.0
  },

  // Line art preset - optimized for line drawings and sketches
  lineart: {
    outputWidth: 100,
    colorMode: 'grayscale',
    dithering: false,
    edgeDetect: true,
    preset: 'lineart',
    enhanceContrast: true,
    aspectRatioCorrection: 0.55,
    invert: false,
    edgeThreshold: 50,
    blur: 0,
    sharpen: 3.0,
    brightness: 1.0,
    saturation: 0.0,
    contrast: 1.5,
    detailLevel: 1.5,
    gamma: 1.2
  },

  // Colorful preset - optimized for vivid, colorful images
  colorful: {
    outputWidth: 120,
    colorMode: 'truecolor',
    dithering: true,
    edgeDetect: false,
    preset: 'detailed',
    enhanceContrast: true,
    aspectRatioCorrection: 0.5,
    invert: false,
    edgeThreshold: 75,
    blur: 0,
    sharpen: 1.5,
    brightness: 1.1,
    saturation: 1.5,
    contrast: 1.2,
    detailLevel: 1.0,
    gamma: 0.9
  },

  // High detail preset - maximum detail preservation
  highdetail: {
    outputWidth: 160,
    colorMode: 'ansi',
    dithering: true,
    edgeDetect: false,
    preset: 'ultra',
    enhanceContrast: true,
    aspectRatioCorrection: 0.5,
    invert: false,
    edgeThreshold: 75,
    blur: 0,
    sharpen: 2.0,
    brightness: 1.0,
    saturation: 1.1,
    contrast: 1.3,
    detailLevel: 1.4,
    gamma: 1.0
  },

  // Braille art preset - for braille dot patterns
  braille: {
    outputWidth: 80,
    colorMode: 'braille',
    dithering: true,
    edgeDetect: true,
    preset: 'classic', // Not used in braille mode
    enhanceContrast: true,
    aspectRatioCorrection: 0.4,
    invert: false,
    edgeThreshold: 60,
    blur: 0,
    sharpen: 2.0,
    brightness: 1.1,
    contrast: 1.4,
    saturation: 1.0,
    detailLevel: 1.0,
    gamma: 1.0
  },

  // Minimal preset - clean, simple output
  minimal: {
    outputWidth: 80,
    colorMode: 'grayscale',
    dithering: false,
    edgeDetect: false,
    preset: 'minimal',
    enhanceContrast: true,
    aspectRatioCorrection: 0.55,
    invert: false,
    edgeThreshold: 75,
    blur: 0.5,
    sharpen: 0,
    brightness: 1.0,
    saturation: 0.8,
    contrast: 1.1,
    detailLevel: 0.8,
    gamma: 1.0
  },

  // HTML mode preset - for web display
  html: {
    outputWidth: 120,
    colorMode: 'html',
    dithering: true,
    edgeDetect: false,
    preset: 'detailed',
    enhanceContrast: true,
    aspectRatioCorrection: 0.5,
    invert: false,
    edgeThreshold: 75,
    blur: 0,
    sharpen: 1.5,
    brightness: 1.0,
    saturation: 1.2,
    contrast: 1.2,
    detailLevel: 1.0,
    gamma: 1.0
  }
}

// Initialize preset dropdown when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  // Add preset dropdown to advanced settings
  const advancedForm = document.querySelector('#advanced-panel .settings-form')

  if (advancedForm) {
    // Create preset group at the top
    const presetGroup = document.createElement('div')
    presetGroup.className = 'form-group'
    presetGroup.innerHTML = `
      <label for="preset-config-select">Quick Presets</label>
      <div class="select-wrapper">
        <select id="preset-config-select">
          <option value="">Custom Settings</option>
          <option value="photo">Photo Optimized</option>
          <option value="lineart">Line Art</option>
          <option value="colorful">Colorful (Truecolor)</option>
          <option value="highdetail">High Detail</option>
          <option value="braille">Braille Pattern</option>
          <option value="minimal">Minimal</option>
          <option value="html">HTML Output</option>
        </select>
      </div>
      <div class="hint">Select a preset to quickly configure optimal settings for different types of images</div>
    `

    // Insert at the top
    advancedForm.insertBefore(presetGroup, advancedForm.firstChild)

    // Add listener for preset selection
    const presetSelect = document.getElementById('preset-config-select')
    presetSelect.addEventListener('change', e => {
      const presetKey = e.target.value

      if (presetKey && PRESETS[presetKey]) {
        applyPreset(PRESETS[presetKey])
      }
    })
  }

  // Create preset quick actions in the sidebar
  addQuickActions()
})

/**
 * Apply a settings preset
 * @param {Object} preset - The preset to apply
 */
function applyPreset(preset) {
  if (!window.app || !preset) return

  // Store current display settings since we don't want to override those
  const displaySettings = {
    fontFamily: window.app.settings.fontFamily,
    fontSize: window.app.settings.fontSize,
    autoFit: window.app.settings.autoFit,
    bgColor: window.app.settings.bgColor,
    textColor: window.app.settings.textColor
  }

  // Apply the preset
  window.app.settings = {...window.app.settings, ...preset, ...displaySettings}

  // Update UI to reflect new settings
  window.app.updateUIFromSettings()

  // Show confirmation
  window.app.showStatus('Preset applied', 'success')
}

/**
 * Add quick action buttons to the sidebar
 */
function addQuickActions() {
  const actionSection = document.createElement('div')
  actionSection.className = 'sidebar-section'
  actionSection.innerHTML = `
    <span class="sidebar-heading">Quick Presets</span>
    <div class="quick-presets">
      <button data-preset="photo" class="preset-btn">Photo</button>
      <button data-preset="lineart" class="preset-btn">Line Art</button>
      <button data-preset="colorful" class="preset-btn">Colorful</button>
      <button data-preset="braille" class="preset-btn">Braille</button>
    </div>
  `

  // Style the preset buttons
  const style = document.createElement('style')
  style.textContent = `
    .quick-presets {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 8px;
    }
    
    .preset-btn {
      flex: 1;
      min-width: 40%;
      padding: 6px 8px;
      border: 1px solid var(--divider);
      border-radius: 4px;
      background-color: var(--bg-tertiary);
      color: var(--text-primary);
      font-size: 0.85rem;
      cursor: pointer;
      transition: background-color 0.2s ease, transform 0.1s ease;
      text-align: center;
    }
    
    .preset-btn:hover {
      background-color: var(--bg-elevated);
      transform: translateY(-1px);
    }
    
    .preset-btn:active {
      transform: translateY(0);
    }
  `

  document.head.appendChild(style)

  // Insert after the first sidebar section
  const firstSection = document.querySelector('.sidebar-section')
  if (firstSection && firstSection.nextSibling) {
    firstSection.parentNode.insertBefore(
      actionSection,
      firstSection.nextSibling
    )

    // Add event listeners
    const presetButtons = document.querySelectorAll('.preset-btn')
    presetButtons.forEach(button => {
      button.addEventListener('click', () => {
        const presetKey = button.dataset.preset
        if (presetKey && PRESETS[presetKey]) {
          applyPreset(PRESETS[presetKey])
        }
      })
    })
  }
}

/**
 * Analyze image and suggest optimal settings
 */
async function analyzeImage() {
  if (!window.app || !window.app.selectedImagePath) return

  window.app.showStatus('Analyzing image...', 'info')
  window.app.showLoading(true)

  // In a real implementation, we would use the Python backend to analyze the image
  // For this demo, we'll simulate it with a timeout
  setTimeout(() => {
    const imagePath = window.app.selectedImagePath

    // Check the file extension to make a basic guess
    const ext = imagePath.toLowerCase().split('.').pop()

    let suggestedPreset

    if (ext === 'png' || ext === 'gif') {
      // PNGs and GIFs are often line art, logos, or graphics
      suggestedPreset = PRESETS.lineart
    } else if (ext === 'jpg' || ext === 'jpeg') {
      // JPEGs are often photos
      suggestedPreset = PRESETS.photo
    } else {
      // Default to high detail
      suggestedPreset = PRESETS.highdetail
    }

    // Apply the suggested preset
    applyPreset(suggestedPreset)

    window.app.showLoading(false)
    window.app.showStatus(
      'Analysis complete. Applied recommended settings.',
      'success'
    )
  }, 1000)
}

// Add analyze button when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  const generateBtn = document.getElementById('generate-btn')

  if (generateBtn) {
    const analyzeBtn = document.createElement('button')
    analyzeBtn.id = 'analyze-btn'
    analyzeBtn.className = 'sidebar-btn'
    analyzeBtn.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
        <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
      </svg>
      Analyze & Suggest
    `
    analyzeBtn.disabled = true

    // Insert before generate button
    generateBtn.parentNode.insertBefore(analyzeBtn, generateBtn)

    // Enable when image is selected
    const originalEnableControls = window.app.enableControls
    window.app.enableControls = function () {
      originalEnableControls.call(window.app)
      document.getElementById('analyze-btn').disabled = false
    }

    // Add click handler
    analyzeBtn.addEventListener('click', analyzeImage)
  }
})

/**
 * Save current settings as custom preset
 */
function saveCustomPreset() {
  if (!window.app) return

  // Prompt for preset name
  const presetName = prompt('Enter a name for your custom preset:')

  if (!presetName) return

  // Get current processing settings (excluding display settings)
  const customPreset = {
    outputWidth: window.app.settings.outputWidth,
    colorMode: window.app.settings.colorMode,
    dithering: window.app.settings.dithering,
    edgeDetect: window.app.settings.edgeDetect,
    preset: window.app.settings.preset,
    enhanceContrast: window.app.settings.enhanceContrast,
    aspectRatioCorrection: window.app.settings.aspectRatioCorrection,
    invert: window.app.settings.invert,
    edgeThreshold: window.app.settings.edgeThreshold,
    blur: window.app.settings.blur,
    sharpen: window.app.settings.sharpen,
    brightness: window.app.settings.brightness,
    saturation: window.app.settings.saturation,
    contrast: window.app.settings.contrast,
    detailLevel: window.app.settings.detailLevel,
    gamma: window.app.settings.gamma
  }

  // In a full implementation, we would save to electron-store
  // For this demo, we'll just add to the PRESETS object
  PRESETS[presetName.toLowerCase()] = customPreset

  // Add to preset dropdown
  const presetSelect = document.getElementById('preset-config-select')
  if (presetSelect) {
    const option = document.createElement('option')
    option.value = presetName.toLowerCase()
    option.textContent = `${presetName} (Custom)`
    presetSelect.appendChild(option)
  }

  window.app.showStatus(`Saved preset "${presetName}"`, 'success')
}

// Add save preset button when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  const advancedPanel = document.getElementById('advanced-panel')

  if (advancedPanel) {
    const savePresetBtn = document.createElement('button')
    savePresetBtn.id = 'save-preset-btn'
    savePresetBtn.className = 'primary-btn'
    savePresetBtn.style.marginTop = '16px'
    savePresetBtn.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path>
        <polyline points="17 21 17 13 7 13 7 21"></polyline>
        <polyline points="7 3 7 8 15 8"></polyline>
      </svg>
      Save Current Settings as Preset
    `

    // Add to the end of advanced panel
    const settingsForm = advancedPanel.querySelector('.settings-form')
    settingsForm.appendChild(savePresetBtn)

    // Add click handler
    savePresetBtn.addEventListener('click', saveCustomPreset)
  }
})
