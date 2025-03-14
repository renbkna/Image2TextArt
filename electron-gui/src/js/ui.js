document.addEventListener('DOMContentLoaded', () => {
  // Modal functionality
  const aboutModal = document.getElementById('about-modal')
  const aboutLink = document.getElementById('about-link')
  const closeButtons = document.getElementsByClassName('modal-close')

  // Open the about modal
  aboutLink.addEventListener('click', e => {
    e.preventDefault()
    aboutModal.style.display = 'block'
  })

  // Close the modal when clicking the X
  for (let button of closeButtons) {
    button.addEventListener('click', () => {
      aboutModal.style.display = 'none'
    })
  }

  // Close the modal when clicking outside of it
  window.addEventListener('click', e => {
    if (e.target === aboutModal) {
      aboutModal.style.display = 'none'
    }
  })

  // Close modal when pressing Escape
  window.addEventListener('keydown', e => {
    if (e.key === 'Escape' && aboutModal.style.display === 'block') {
      aboutModal.style.display = 'none'
    }
  })

  // GitHub link handler
  document.getElementById('github-link').addEventListener('click', e => {
    e.preventDefault()
    const {ipcRenderer} = require('electron')
    ipcRenderer.invoke(
      'open-external-url',
      'https://github.com/renbkna/Image2TextArt'
    )
  })
})
