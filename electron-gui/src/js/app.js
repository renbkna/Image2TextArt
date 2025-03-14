const {ipcRenderer} = require('electron')
const path = require('path')
const Convert = require('ansi-to-html')
const convert = new Convert({
  fg: '#fff',
  bg: '#000',
  newline: true,
  escapeXML: false,
  stream: false
})

// Main application class
class AsciiArtGenerator {
  constructor() {
    this.selectedImagePath = null
    this.asciiOutput = null
    this.isProcessing = false
    this.zoomLevel = 100
    this.settings = {
      outputWidth: 100,
      colorMode: 'ansi',
      dithering: false,
      edgeDetect: false,
      preset: 'classic',
      enhanceContrast: true,
      aspectRatioCorrection: 0.55,
      invert: false,
      edgeThreshold: 75,
      blur: 0,
      sharpen: 0,
      brightness: 1.0,
      saturation: 1.0,
      contrast: 1.0,
      detailLevel: 1.0,
      gamma: 1.0,
      customChars: '',
      // Display settings (not sent to Python)
      fontFamily: 'monospace',
      fontSize: 14,
      autoFit: true,
      bgColor: '#000000',
      textColor: '#ffffff'
    }

    // Initialize the application
    this.init()
  }

  /**
   * Initialize the application
   */
  async init() {
    await this.loadSettings()
    this.setupEventListeners()
    this.updateUIFromSettings()
  }

  /**
   * Load saved settings from Electron store
   */
  async loadSettings() {
    try {
      const {lastSettings, darkMode} = await ipcRenderer.invoke('get-settings')

      // Load saved settings
      if (lastSettings) {
        this.settings = {...this.settings, ...lastSettings}
      }

      // Apply theme
      if (darkMode !== undefined) {
        document.body.classList.toggle('light-theme', !darkMode)
        document.getElementById('light-icon').style.display = darkMode
          ? 'none'
          : 'block'
        document.getElementById('dark-icon').style.display = darkMode
          ? 'block'
          : 'none'
      }
    } catch (error) {
      console.error('Error loading settings:', error)
    }
  }

  /**
   * Setup all event listeners
   */
  setupEventListeners() {
    // Window control buttons
    document.getElementById('minimize-btn').addEventListener('click', () => {
      ipcRenderer.invoke('minimize-window')
    })

    document
      .getElementById('maximize-btn')
      .addEventListener('click', async () => {
        const isMaximized = await ipcRenderer.invoke('maximize-window')
        // Update maximize button icon based on window state
        // You can add logic here to change the icon if needed
      })

    document.getElementById('close-btn').addEventListener('click', () => {
      ipcRenderer.invoke('close-window')
    })

    // Image selection
    document
      .getElementById('select-image-btn')
      .addEventListener('click', () => {
        this.selectImage()
      })

    // Tab switching
    const tabButtons = document.querySelectorAll('[data-tab]')
    tabButtons.forEach(button => {
      button.addEventListener('click', e => {
        const tabId = e.currentTarget.dataset.tab
        this.switchTab(tabId)
      })
    })

    // Generate button
    document.getElementById('generate-btn').addEventListener('click', () => {
      this.generateAsciiArt()
    })

    // Save button
    document.getElementById('save-btn').addEventListener('click', () => {
      this.saveOutput()
    })

    // Copy button
    document.getElementById('copy-btn').addEventListener('click', () => {
      this.copyToClipboard()
    })

    // Theme toggle
    document
      .getElementById('theme-toggle-btn')
      .addEventListener('click', () => {
        const isDarkMode = !document.body.classList.contains('light-theme')
        document.body.classList.toggle('light-theme')

        // Toggle icons
        document.getElementById('light-icon').style.display = isDarkMode
          ? 'none'
          : 'block'
        document.getElementById('dark-icon').style.display = isDarkMode
          ? 'block'
          : 'none'

        // Save theme preference
        ipcRenderer.invoke('toggle-dark-mode', isDarkMode)
      })

    // GitHub link
    document.getElementById('github-link').addEventListener('click', e => {
      e.preventDefault()
      ipcRenderer.invoke(
        'open-external-url',
        'https://github.com/renbkna/ansi-ascii-art-generator'
      )
    })

    // Setup all form control events
    this.setupFormControls()
  }

  /**
   * Setup all form control event listeners
   */
  setupFormControls() {
    // Basic settings
    document.getElementById('width-input').addEventListener('change', e => {
      this.settings.outputWidth = parseInt(e.target.value)
    })

    document
      .getElementById('color-mode-select')
      .addEventListener('change', e => {
        this.settings.colorMode = e.target.value
      })

    document.getElementById('preset-select').addEventListener('change', e => {
      this.settings.preset = e.target.value
    })

    document
      .getElementById('aspect-ratio-slider')
      .addEventListener('input', e => {
        this.settings.aspectRatioCorrection = parseFloat(e.target.value)
        document.getElementById('aspect-ratio-value').textContent =
          e.target.value
      })

    document
      .getElementById('dithering-checkbox')
      .addEventListener('change', e => {
        this.settings.dithering = e.target.checked
      })

    document
      .getElementById('edge-detect-checkbox')
      .addEventListener('change', e => {
        this.settings.edgeDetect = e.target.checked
      })

    document
      .getElementById('enhance-contrast-checkbox')
      .addEventListener('change', e => {
        this.settings.enhanceContrast = e.target.checked
      })

    document.getElementById('invert-checkbox').addEventListener('change', e => {
      this.settings.invert = e.target.checked
    })

    // Advanced settings
    document
      .getElementById('edge-threshold-slider')
      .addEventListener('input', e => {
        this.settings.edgeThreshold = parseInt(e.target.value)
        document.getElementById('edge-threshold-value').textContent =
          e.target.value
      })

    document.getElementById('blur-slider').addEventListener('input', e => {
      this.settings.blur = parseFloat(e.target.value)
      document.getElementById('blur-value').textContent = e.target.value
    })

    document.getElementById('sharpen-slider').addEventListener('input', e => {
      this.settings.sharpen = parseFloat(e.target.value)
      document.getElementById('sharpen-value').textContent = e.target.value
    })

    document
      .getElementById('brightness-slider')
      .addEventListener('input', e => {
        this.settings.brightness = parseFloat(e.target.value)
        document.getElementById('brightness-value').textContent = e.target.value
      })

    document
      .getElementById('saturation-slider')
      .addEventListener('input', e => {
        this.settings.saturation = parseFloat(e.target.value)
        document.getElementById('saturation-value').textContent = e.target.value
      })

    document.getElementById('contrast-slider').addEventListener('input', e => {
      this.settings.contrast = parseFloat(e.target.value)
      document.getElementById('contrast-value').textContent = e.target.value
    })

    document
      .getElementById('detail-level-slider')
      .addEventListener('input', e => {
        this.settings.detailLevel = parseFloat(e.target.value)
        document.getElementById('detail-level-value').textContent =
          e.target.value
      })

    document.getElementById('gamma-slider').addEventListener('input', e => {
      this.settings.gamma = parseFloat(e.target.value)
      document.getElementById('gamma-value').textContent = e.target.value
    })

    document
      .getElementById('custom-chars-input')
      .addEventListener('change', e => {
        this.settings.customChars = e.target.value
      })

    // Display settings
    document
      .getElementById('font-family-select')
      .addEventListener('change', e => {
        this.settings.fontFamily = e.target.value
        this.updateOutputDisplay()
      })

    document.getElementById('font-size-input').addEventListener('change', e => {
      this.settings.fontSize = parseInt(e.target.value)
      this.updateOutputDisplay()
    })

    document
      .getElementById('auto-fit-checkbox')
      .addEventListener('change', e => {
        this.settings.autoFit = e.target.checked

        // Update output display which will handle toggle of auto-fit class
        this.updateOutputDisplay()
      })

    document.getElementById('bg-color-picker').addEventListener('change', e => {
      this.settings.bgColor = e.target.value
      document.getElementById('bg-color-text').textContent = e.target.value
      this.updateOutputDisplay()
    })

    document
      .getElementById('text-color-picker')
      .addEventListener('change', e => {
        this.settings.textColor = e.target.value
        document.getElementById('text-color-text').textContent = e.target.value
        this.updateOutputDisplay()
      })

    // Zoom controls
    document.getElementById('zoom-in-btn').addEventListener('click', () => {
      this.zoomIn()
    })

    document.getElementById('zoom-out-btn').addEventListener('click', () => {
      this.zoomOut()
    })

    document.getElementById('zoom-reset-btn').addEventListener('click', () => {
      this.resetZoom()
    })

    // Number input buttons
    const numberInputs = document.querySelectorAll('.input-with-buttons')
    numberInputs.forEach(container => {
      const input = container.querySelector('input[type="number"]')
      const minusBtn = container.querySelector('.minus')
      const plusBtn = container.querySelector('.plus')

      minusBtn.addEventListener('click', () => {
        input.value = Math.max(
          parseInt(input.min) || 0,
          parseInt(input.value) - 1
        )
        input.dispatchEvent(new Event('change'))
      })

      plusBtn.addEventListener('click', () => {
        input.value = Math.min(
          parseInt(input.max) || Infinity,
          parseInt(input.value) + 1
        )
        input.dispatchEvent(new Event('change'))
      })
    })
  }

  /**
   * Update UI controls to reflect current settings
   */
  updateUIFromSettings() {
    // Basic settings
    document.getElementById('width-input').value = this.settings.outputWidth
    document.getElementById('color-mode-select').value = this.settings.colorMode
    document.getElementById('preset-select').value = this.settings.preset
    document.getElementById('aspect-ratio-slider').value =
      this.settings.aspectRatioCorrection
    document.getElementById('aspect-ratio-value').textContent =
      this.settings.aspectRatioCorrection
    document.getElementById('dithering-checkbox').checked =
      this.settings.dithering
    document.getElementById('edge-detect-checkbox').checked =
      this.settings.edgeDetect
    document.getElementById('enhance-contrast-checkbox').checked =
      this.settings.enhanceContrast
    document.getElementById('invert-checkbox').checked = this.settings.invert

    // Advanced settings
    document.getElementById('edge-threshold-slider').value =
      this.settings.edgeThreshold
    document.getElementById('edge-threshold-value').textContent =
      this.settings.edgeThreshold
    document.getElementById('blur-slider').value = this.settings.blur
    document.getElementById('blur-value').textContent = this.settings.blur
    document.getElementById('sharpen-slider').value = this.settings.sharpen
    document.getElementById('sharpen-value').textContent = this.settings.sharpen
    document.getElementById('brightness-slider').value =
      this.settings.brightness
    document.getElementById('brightness-value').textContent =
      this.settings.brightness
    document.getElementById('saturation-slider').value =
      this.settings.saturation
    document.getElementById('saturation-value').textContent =
      this.settings.saturation
    document.getElementById('contrast-slider').value = this.settings.contrast
    document.getElementById('contrast-value').textContent =
      this.settings.contrast
    document.getElementById('detail-level-slider').value =
      this.settings.detailLevel
    document.getElementById('detail-level-value').textContent =
      this.settings.detailLevel
    document.getElementById('gamma-slider').value = this.settings.gamma
    document.getElementById('gamma-value').textContent = this.settings.gamma
    document.getElementById('custom-chars-input').value =
      this.settings.customChars || ''

    // Display settings
    document.getElementById('font-family-select').value =
      this.settings.fontFamily
    document.getElementById('font-size-input').value = this.settings.fontSize
    document.getElementById('auto-fit-checkbox').checked = this.settings.autoFit
    document.getElementById('bg-color-picker').value = this.settings.bgColor
    document.getElementById('bg-color-text').textContent = this.settings.bgColor
    document.getElementById('text-color-picker').value = this.settings.textColor
    document.getElementById('text-color-text').textContent =
      this.settings.textColor
  }

  /**
   * Switch between settings tabs
   * @param {string} tabId - The ID of the tab to switch to
   */
  switchTab(tabId) {
    // Hide all panels
    document.querySelectorAll('.settings-panel').forEach(panel => {
      panel.classList.remove('active')
    })

    // Show the selected panel
    document.getElementById(tabId).classList.add('active')

    // Update tab button states
    document.querySelectorAll('.sidebar-btn[data-tab]').forEach(btn => {
      btn.classList.remove('active')
    })

    document
      .querySelector(`.sidebar-btn[data-tab="${tabId}"]`)
      .classList.add('active')
  }

  /**
   * Select an image file
   */
  async selectImage() {
    try {
      const filePath = await ipcRenderer.invoke('select-file')

      if (filePath) {
        this.selectedImagePath = filePath
        this.updateImagePreview(filePath)
        this.updateImageInfo(filePath)
        this.enableControls()
      }
    } catch (error) {
      console.error('Error selecting image:', error)
      this.showStatus('Error selecting image', 'error')
    }
  }

  /**
   * Update the image preview
   * @param {string} filePath - Path to the image
   */
  updateImagePreview(filePath) {
    const previewImg = document.getElementById('preview-image')
    const emptyPreview = document.getElementById('empty-preview')

    // Convert file path to file URL
    const fileUrl = `file://${filePath}`

    // Update image preview
    previewImg.src = fileUrl
    previewImg.style.display = 'block'
    emptyPreview.style.display = 'none'
  }

  /**
   * Update the image information display
   * @param {string} filePath - Path to the image
   */
  updateImageInfo(filePath) {
    const imageInfo = document.getElementById('image-info')
    const fileName = path.basename(filePath)

    imageInfo.textContent = fileName
  }

  /**
   * Enable UI controls after an image is selected
   */
  enableControls() {
    document.getElementById('generate-btn').disabled = false
  }

  /**
   * Generate ASCII art from the selected image
   */
  async generateAsciiArt() {
    if (!this.selectedImagePath || this.isProcessing) {
      return
    }

    try {
      this.isProcessing = true
      this.showLoading(true)

      // Get current settings for processing
      const processingSettings = {...this.settings}

      // Send to main process for Python execution
      this.asciiOutput = await ipcRenderer.invoke(
        'process-image',
        this.selectedImagePath,
        processingSettings
      )

      // Update the output display
      this.updateOutputDisplay()

      // Enable save and copy buttons
      document.getElementById('save-btn').disabled = false
      document.getElementById('copy-btn').disabled = false

      // Show success message
      this.showStatus('ASCII art generated successfully', 'success')

      // Save settings
      await ipcRenderer.invoke('save-settings', this.settings)
    } catch (error) {
      console.error('Error generating ASCII art:', error)
      this.showStatus('Error generating ASCII art', 'error')
    } finally {
      this.isProcessing = false
      this.showLoading(false)
    }
  }

  /**
   * Update the output display with the generated ASCII art
   */
  updateOutputDisplay() {
    const outputArea = document.getElementById('output-area')
    const emptyOutput = document.getElementById('empty-output')
    const outputContainer = document.querySelector('.output-container')

    if (this.asciiOutput) {
      // Show the output
      outputArea.style.display = 'block'
      emptyOutput.style.display = 'none'

      // Reset classes on the container
      outputContainer.className = 'output-container'

      // Add mode-specific class
      outputContainer.classList.add(`${this.settings.colorMode}-mode`)

      // Apply auto-fit if enabled
      if (this.settings.autoFit) {
        outputContainer.classList.add('auto-fit')
      }

      // Apply display settings
      outputArea.style.fontFamily = this.settings.fontFamily
      outputArea.style.fontSize = `${this.settings.fontSize}px`
      outputArea.style.backgroundColor = this.settings.bgColor

      // Handle different color modes
      try {
        if (this.settings.colorMode === 'grayscale') {
          // For grayscale, apply custom text color
          outputArea.innerHTML = ''
          outputArea.textContent = this.asciiOutput
          outputArea.style.color = this.settings.textColor
        } else if (this.settings.colorMode === 'html') {
          // For HTML output, use innerHTML to render properly
          outputArea.innerHTML = this.asciiOutput
        } else if (
          this.settings.colorMode === 'ansi' ||
          this.settings.colorMode === 'truecolor'
        ) {
          // For ANSI/truecolor, convert ANSI properly
          outputArea.innerHTML = ''
          outputArea.innerHTML = this.processAnsiOutput(this.asciiOutput)
        } else {
          // For all other modes including braille
          outputArea.innerHTML = ''
          outputArea.textContent = this.asciiOutput
          outputArea.style.color = '#ffffff'
        }

        // Apply auto-fit if needed
        outputContainer.classList.toggle('auto-fit', this.settings.autoFit)

        if (this.settings.autoFit) {
          this.applyAutoFit()
        } else {
          outputArea.style.transform = 'none'
        }
      } catch (error) {
        console.error('Error rendering output:', error)
        // Fallback to plain text if rendering fails
        outputArea.textContent = this.asciiOutput
      }
    }
  }

  /**
   * Process ANSI output for display
   * @param {string} ansi - Raw ANSI text
   * @returns {string} - Processed HTML
   */
  processAnsiOutput(ansi) {
    // Create a temporary div to hold the content
    const tempDiv = document.createElement('div')

    // Strip problematic characters and replace with spans
    let processed = ansi
      // Replace newlines with breaks
      .replace(/\r?\n/g, '<br>')

      // Replace ANSI color codes with spans
      .replace(/\u001b\[([0-9;]*)m/g, (match, p1) => {
        // Parse the ANSI parameters
        const params = p1.split(';').map(Number)

        if (params[0] === 0) {
          return '</span>' // Reset
        }

        // Handle foreground colors
        if (params[0] === 38) {
          if (params[1] === 5) {
            // 256 color mode
            return `<span style="color: var(--ansi-${params[2] || 7});">`
          } else if (params[1] === 2) {
            // RGB color mode
            return `<span style="color: rgb(${params[2] || 255}, ${
              params[3] || 255
            }, ${params[4] || 255});">`
          }
        }

        // Default styling
        return `<span>`
      })

    // Ensure all spans are properly closed
    const openTags = (processed.match(/<span/g) || []).length
    const closeTags = (processed.match(/<\/span>/g) || []).length

    // Add any missing closing tags
    for (let i = 0; i < openTags - closeTags; i++) {
      processed += '</span>'
    }

    return processed
  }

  /**
   * Convert ANSI escape sequences to HTML
   * @param {string} ansi - ANSI escaped text
   * @returns {string} - HTML formatted text
   */
  convertAnsiToHTML(ansi) {
    try {
      // Replace problematic newlines with <br>
      ansi = ansi.replace(/\r?\n/g, '<br>')

      // Use a more direct approach to handle ANSI codes
      // We need this for compatibility with truecolor output

      // Replace foreground colors
      ansi = ansi
        // Handle reset
        .replace(/\u001b\[0m/g, '</span>')

        // Handle 256 color mode
        .replace(/\u001b\[38;5;(\d+)m/g, (match, color) => {
          return `<span style="color: var(--color-${color || 7});">`
        })

        // Handle truecolor RGB mode
        .replace(/\u001b\[38;2;(\d+);(\d+);(\d+)m/g, (match, r, g, b) => {
          return `<span style="color: rgb(${r || 255}, ${g || 255}, ${
            b || 255
          });">`
        })

      // Add the basic ANSI color stylesheet if not already added
      if (!document.getElementById('ansi-colors-style')) {
        const styleEl = document.createElement('style')
        styleEl.id = 'ansi-colors-style'
        styleEl.textContent = this.generateAnsiStyles()
        document.head.appendChild(styleEl)
      }

      return ansi
    } catch (error) {
      console.error('Error converting ANSI to HTML:', error)
      // Fallback to plain text if conversion fails
      return ansi.replace(/\u001b\[[0-9;]*[a-zA-Z]/g, '')
    }
  }

  /**
   * Generate CSS for ANSI colors
   * @returns {string} - CSS style rules
   */
  generateAnsiStyles() {
    // Basic ANSI colors
    const colors = [
      '#000000',
      '#800000',
      '#008000',
      '#808000', // Black, Red, Green, Yellow
      '#000080',
      '#800080',
      '#008080',
      '#c0c0c0', // Blue, Magenta, Cyan, White
      '#808080',
      '#ff0000',
      '#00ff00',
      '#ffff00', // Gray, Bright Red, Bright Green, Bright Yellow
      '#0000ff',
      '#ff00ff',
      '#00ffff',
      '#ffffff' // Bright Blue, Bright Magenta, Bright Cyan, Bright White
    ]

    let css = ''
    // Add base styles
    css += `
      #output-area { line-height: 1.2; }
      #output-area span { display: inline; }
      #output-area br { display: block; height: 0; }
    `

    // Add color variables
    for (let i = 0; i < colors.length; i++) {
      css += `--color-${i}: ${colors[i]}; `
    }

    // Add 256 color palette - just add a few examples for compactness
    for (let i = 16; i < 256; i++) {
      // This is a simplification - a full implementation would calculate all 256 colors
      if (i < 20) {
        // Just for example
        css += `--color-${i}: hsl(${i * 8}, 100%, 50%); `
      }
    }

    return `:root { ${css} }`
  }

  /**
   * Apply auto-fit scaling to the output
   */
  applyAutoFit() {
    if (!this.asciiOutput) return

    const outputArea = document.getElementById('output-area')
    const container = document.querySelector('.output-container')

    // Reset transform first and measure content
    outputArea.style.transform = 'none'

    // Wait for browser to recalculate dimensions
    setTimeout(() => {
      // Get dimensions after forced reflow
      const containerWidth = container.clientWidth - 32 // Account for padding
      const containerHeight = container.clientHeight - 32 // Account for padding
      const contentWidth = outputArea.scrollWidth
      const contentHeight = outputArea.scrollHeight

      // Calculate scale ratios
      const widthRatio = containerWidth / contentWidth
      const heightRatio = containerHeight / contentHeight

      // Use the smaller ratio for scaling
      const scale = Math.min(widthRatio, heightRatio) * 0.95 // 0.95 to leave some margin

      // Always apply the transform
      outputArea.style.transform = `scale(${scale})`
      outputArea.style.transformOrigin = 'top left'
    }, 0)
  }

  /**
   * Save the ASCII output to a file
   */
  async saveOutput() {
    if (!this.asciiOutput) return

    try {
      const defaultFileName =
        path.basename(
          this.selectedImagePath,
          path.extname(this.selectedImagePath)
        ) + '.txt'
      const savedPath = await ipcRenderer.invoke(
        'save-file',
        defaultFileName,
        this.asciiOutput
      )

      if (savedPath) {
        this.showStatus(`Saved to ${path.basename(savedPath)}`, 'success')
      }
    } catch (error) {
      console.error('Error saving output:', error)
      this.showStatus('Error saving file', 'error')
    }
  }

  /**
   * Copy the ASCII output to clipboard
   */
  copyToClipboard() {
    if (!this.asciiOutput) return

    try {
      navigator.clipboard.writeText(this.asciiOutput)
      this.showStatus('Copied to clipboard', 'success')
    } catch (error) {
      console.error('Error copying to clipboard:', error)
      this.showStatus('Error copying to clipboard', 'error')
    }
  }

  /**
   * Show loading overlay
   * @param {boolean} show - Whether to show or hide the loading overlay
   */
  showLoading(show) {
    const loadingOverlay = document.getElementById('loading-overlay')
    loadingOverlay.style.display = show ? 'flex' : 'none'
  }

  /**
   * Show status message
   * @param {string} message - The message to show
   * @param {string} type - The type of message ('success' or 'error')
   */
  showStatus(message, type = 'info') {
    const statusEl = document.getElementById('status-message')
    statusEl.textContent = message
    statusEl.className = 'status-message'

    if (type) {
      statusEl.classList.add(type)
    }

    // Auto-clear after 5 seconds
    setTimeout(() => {
      statusEl.textContent = ''
      statusEl.className = 'status-message'
    }, 5000)
  }

  /**
   * Zoom in the output
   */
  zoomIn() {
    const levels = [50, 75, 100, 125, 150, 200]
    const currentIndex = levels.indexOf(this.zoomLevel)

    if (currentIndex < levels.length - 1) {
      this.zoomLevel = levels[currentIndex + 1]
      this.applyZoom()
    }
  }

  /**
   * Zoom out the output
   */
  zoomOut() {
    const levels = [50, 75, 100, 125, 150, 200]
    const currentIndex = levels.indexOf(this.zoomLevel)

    if (currentIndex > 0) {
      this.zoomLevel = levels[currentIndex - 1]
      this.applyZoom()
    }
  }

  /**
   * Reset zoom to 100%
   */
  resetZoom() {
    this.zoomLevel = 100
    this.applyZoom()
  }

  /**
   * Apply the current zoom level
   */
  applyZoom() {
    const outputContainer = document.querySelector('.output-container')

    // Remove all zoom classes
    outputContainer.classList.remove(
      'zoom-50',
      'zoom-75',
      'zoom-100',
      'zoom-125',
      'zoom-150',
      'zoom-200'
    )

    // Add the current zoom class
    outputContainer.classList.add(`zoom-${this.zoomLevel}`)

    // If auto-fit is enabled, reapply it
    if (this.settings.autoFit) {
      this.applyAutoFit()
    }
  }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.app = new AsciiArtGenerator()
})
