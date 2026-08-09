import * as api from '../api.js';
import { addConsoleLog } from '../logger.js';

export function setCalendarSelectedMedia(media) {
  const mediaIdInput = document.getElementById('calendar-media-id');
  const mediaBox = document.getElementById('calendar-media-selected-box');
  const previewImg = document.getElementById('calendar-media-preview-img');
  const filenameDiv = document.getElementById('calendar-media-filename');
  const filesizeDiv = document.getElementById('calendar-media-filesize');

  if (!media) {
    if (mediaIdInput) mediaIdInput.value = '';
    if (mediaBox) mediaBox.classList.add('hidden');
    return;
  }

  if (mediaIdInput) mediaIdInput.value = media.id;
  if (filenameDiv) filenameDiv.textContent = media.original_name || media.filename;
  if (filesizeDiv) {
    const kb = Math.round(media.file_size / 1024);
    filesizeDiv.textContent = kb > 1024 ? `${(kb / 1024).toFixed(1)} MB` : `${kb} KB`;
  }
  if (previewImg) {
    if (media.mime_type.startsWith('video/')) {
      previewImg.src = '/static/img/video-icon.png';
      previewImg.onerror = () => { previewImg.src = ''; };
    } else {
      previewImg.src = media.url;
    }
  }
  if (mediaBox) mediaBox.classList.remove('hidden');
}

export async function renderMediaLibraryGrid(targetGridId = 'media-library-grid') {
  const grid = document.getElementById(targetGridId);
  const badge = document.getElementById(targetGridId === 'tab-media-library-grid' ? 'tab-media-count-badge' : 'media-count-badge');
  if (!grid) return;

  grid.innerHTML = '<div style="font-size: 0.75rem; color: var(--text-muted); grid-column: 1/-1; text-align: center;">Carregando mídias...</div>';

  try {
    const mediaList = await api.getUserMediaAPI();
    if (badge) badge.textContent = `${mediaList.length} mídias`;

    if (mediaList.length === 0) {
      grid.innerHTML = '<div style="font-size: 0.75rem; color: var(--text-muted); grid-column: 1/-1; text-align: center; padding: 1.5rem;">Nenhuma mídia enviada ainda. Faça o upload acima!</div>';
      return;
    }

    grid.innerHTML = '';
    mediaList.forEach(item => {
      const card = document.createElement('div');
      card.className = 'media-item-card';
      card.style.cssText = 'border: 1px solid var(--border-color); border-radius: var(--radius-md); overflow: hidden; background: var(--bg-surface); display: flex; flex-direction: column; position: relative; transition: transform 0.15s ease;';

      const isVideo = item.mime_type.startsWith('video/');
      const mediaPreview = isVideo
        ? `<div style="height: 90px; background: #000; display: flex; align-items: center; justify-content: center; color: #fff; font-size: 0.7rem;">🎬 Vídeo</div>`
        : `<img src="${item.url}" alt="${item.original_name}" style="height: 90px; width: 100%; object-fit: cover;">`;

      const kb = Math.round(item.file_size / 1024);
      const sizeStr = kb > 1024 ? `${(kb / 1024).toFixed(1)} MB` : `${kb} KB`;

      card.innerHTML = `
        ${mediaPreview}
        <div style="padding: 0.45rem; font-size: 0.65rem; flex: 1; display: flex; flex-direction: column; justify-content: space-between;">
          <div style="font-weight: 600; color: var(--text-primary); text-overflow: ellipsis; overflow: hidden; white-space: nowrap;" title="${item.original_name}">${item.original_name}</div>
          <div style="color: var(--text-muted); font-size: 0.6rem; margin-bottom: 0.35rem;">${sizeStr}</div>
          <div style="display: flex; gap: 0.25rem;">
            <button type="button" class="btn-select-media btn-primary" data-id="${item.id}" style="flex: 1; font-size: 0.6rem; padding: 0.2rem 0.3rem;">Anexar</button>
            <button type="button" class="btn-delete-media" data-id="${item.id}" style="background: none; border: 1px solid var(--border-color); color: #F43F5E; border-radius: 4px; padding: 0.2rem 0.3rem; font-size: 0.6rem; cursor: pointer;">🗑️ Excluir</button>
          </div>
        </div>
      `;

      // Select button listener
      const selectBtn = card.querySelector('.btn-select-media');
      selectBtn.addEventListener('click', () => {
        setCalendarSelectedMedia(item);
        const modal = document.getElementById('media-library-modal');
        if (modal) modal.classList.add('hidden');
        addConsoleLog(`Mídia "${item.original_name}" selecionada para o agendamento.`, 'sucesso');
        // Open calendar form if not open
        const calendarModal = document.getElementById('calendar-form-modal');
        if (calendarModal && calendarModal.classList.contains('hidden')) {
          const btnOpenCal = document.getElementById('btn-open-calendar-form');
          if (btnOpenCal) btnOpenCal.click();
        }
      });

      // Delete button listener
      const deleteBtn = card.querySelector('.btn-delete-media');
      deleteBtn.addEventListener('click', async (e) => {
        e.stopPropagation();
        if (confirm(`Deseja excluir a mídia "${item.original_name}"?`)) {
          try {
            await api.deleteMediaAPI(item.id);
            addConsoleLog(`Mídia "${item.original_name}" excluída com sucesso.`, 'sucesso');
            renderMediaLibraryGrid('media-library-grid');
            renderMediaLibraryGrid('tab-media-library-grid');
          } catch (err) {
            addConsoleLog(`Erro ao excluir mídia: ${err.message}`, 'erro');
          }
        }
      });

      grid.appendChild(card);
    });
  } catch (error) {
    grid.innerHTML = `<div style="font-size: 0.75rem; color: #F43F5E; grid-column: 1/-1; text-align: center;">Erro: ${error.message}</div>`;
  }
}

export function setupMediaEvents() {
  const modal = document.getElementById('media-library-modal');
  const btnClose = document.getElementById('btn-close-media-library');
  const btnOpenGalleryPicker = document.getElementById('btn-open-gallery-picker');
  const btnOpenHeaderGallery = document.getElementById('btn-open-media-gallery-header');

  if (btnOpenHeaderGallery && modal) {
    btnOpenHeaderGallery.addEventListener('click', () => {
      renderMediaLibraryGrid('media-library-grid');
      modal.classList.remove('hidden');
    });
  }

  const dropzone = document.getElementById('media-upload-dropzone');

  const fileInput = document.getElementById('media-file-input');

  const tabDropzone = document.getElementById('tab-media-upload-dropzone');
  const tabFileInput = document.getElementById('tab-media-file-input');

  const btnUploadDirect = document.getElementById('btn-upload-direct-media');
  const directFileInput = document.getElementById('calendar-direct-file-input');
  const btnRemoveMedia = document.getElementById('btn-remove-calendar-media');

  if (btnOpenGalleryPicker && modal) {
    btnOpenGalleryPicker.addEventListener('click', () => {
      renderMediaLibraryGrid('media-library-grid');
      modal.classList.remove('hidden');
    });
  }

  if (btnClose && modal) {
    btnClose.addEventListener('click', () => {
      modal.classList.add('hidden');
    });
    modal.addEventListener('click', (e) => {
      if (e.target === modal) modal.classList.add('hidden');
    });
  }

  // Upload in modal dropzone
  if (dropzone && fileInput) {
    dropzone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', async (e) => {
      const file = e.target.files[0];
      if (!file) return;
      try {
        addConsoleLog(`Enviando arquivo ${file.name}...`, 'info');
        await api.uploadMediaAPI(file);
        addConsoleLog(`Upload de ${file.name} concluído com sucesso!`, 'sucesso');
        fileInput.value = '';
        renderMediaLibraryGrid('media-library-grid');
        renderMediaLibraryGrid('tab-media-library-grid');
      } catch (err) {
        addConsoleLog(`Erro no upload: ${err.message}`, 'erro');
        alert(err.message);
      }
    });
  }

  // Upload in tab dropzone
  if (tabDropzone && tabFileInput) {
    tabDropzone.addEventListener('click', () => tabFileInput.click());
    tabFileInput.addEventListener('change', async (e) => {
      const file = e.target.files[0];
      if (!file) return;
      try {
        addConsoleLog(`Enviando arquivo ${file.name}...`, 'info');
        await api.uploadMediaAPI(file);
        addConsoleLog(`Upload de ${file.name} concluído com sucesso!`, 'sucesso');
        tabFileInput.value = '';
        renderMediaLibraryGrid('tab-media-library-grid');
        renderMediaLibraryGrid('media-library-grid');
      } catch (err) {
        addConsoleLog(`Erro no upload: ${err.message}`, 'erro');
        alert(err.message);
      }
    });
  }

  // Direct Upload from Calendar modal
  if (btnUploadDirect && directFileInput) {
    btnUploadDirect.addEventListener('click', () => directFileInput.click());
    directFileInput.addEventListener('change', async (e) => {
      const file = e.target.files[0];
      if (!file) return;
      try {
        addConsoleLog(`Enviando arquivo ${file.name}...`, 'info');
        const uploaded = await api.uploadMediaAPI(file);
        addConsoleLog(`Upload de ${file.name} concluído com sucesso!`, 'sucesso');
        directFileInput.value = '';
        setCalendarSelectedMedia(uploaded);
        renderMediaLibraryGrid('tab-media-library-grid');
      } catch (err) {
        addConsoleLog(`Erro no upload: ${err.message}`, 'erro');
        alert(err.message);
      }
    });
  }

  // Remove media button
  if (btnRemoveMedia) {
    btnRemoveMedia.addEventListener('click', () => {
      setCalendarSelectedMedia(null);
    });
  }
}

