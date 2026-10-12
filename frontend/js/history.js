const STORAGE_KEY = "omnistream_downloads_history_v1";

const HistoryManager = {
  getHistory() {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      return data ? JSON.parse(data) : [];
    } catch (e) {
      console.error("Failed to load history from storage", e);
      return [];
    }
  },

  addItem(item) {
    try {
      const history = this.getHistory();
      const newItem = {
        id: "dl_" + Date.now() + "_" + Math.random().toString(36).substring(2, 7),
        title: item.title || "Untitled Media",
        platform: item.platform || "universal",
        type: item.type || "video", // video, audio, image
        quality: item.quality || "best",
        filename: item.filename || "download",
        fileSize: item.fileSize || 0,
        thumbnail: item.thumbnail || "",
        timestamp: new Date().toISOString(),
        downloadUrl: item.downloadUrl || ""
      };
      
      // Keep up to 50 recent items
      history.unshift(newItem);
      if (history.length > 50) history.pop();
      
      localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
      this.updateBadge();
      return newItem;
    } catch (e) {
      console.error("Failed to save item to history", e);
      return null;
    }
  },

  clearHistory() {
    try {
      localStorage.removeItem(STORAGE_KEY);
      this.updateBadge();
      this.render();
    } catch (e) {
      console.error("Failed to clear history", e);
    }
  },

  formatBytes(bytes, decimals = 2) {
    if (!bytes || bytes === 0) return "Direct Stream";
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
  },

  formatDate(isoString) {
    try {
      const d = new Date(isoString);
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + ", " + d.toLocaleDateString();
    } catch {
      return "Recently";
    }
  },

  updateBadge() {
    const history = this.getHistory();
    const badges = document.querySelectorAll(".history-count-badge");
    badges.forEach(b => {
      b.textContent = history.length;
      if (history.length > 0) {
        b.classList.remove("hidden");
      } else {
        b.classList.add("hidden");
      }
    });
  },

  render() {
    const listEl = document.getElementById("history-list");
    if (!listEl) return;

    const history = this.getHistory();
    if (history.length === 0) {
      listEl.innerHTML = `
        <div class="py-16 text-center text-slate-400">
          <i data-lucide="inbox" class="w-12 h-12 mx-auto mb-3 opacity-40"></i>
          <p class="font-medium text-slate-300">No downloads yet</p>
          <p class="text-xs text-slate-500 mt-1">Files you download will appear here for easy access.</p>
        </div>
      `;
      if (window.lucide) window.lucide.createIcons();
      return;
    }

    listEl.innerHTML = history.map(item => {
      const isAudio = item.type === "audio" || (item.filename && item.filename.endsWith(".mp3"));
      const isImage = item.type === "image";
      const icon = isAudio ? "music" : isImage ? "image" : "video";
      const badgeColor = isAudio ? "bg-fuchsia-500/20 text-fuchsia-300 border-fuchsia-500/30" :
                         isImage ? "bg-amber-500/20 text-amber-300 border-amber-500/30" :
                         "bg-indigo-500/20 text-indigo-300 border-indigo-500/30";

      return `
        <div class="flex items-start gap-3 p-3 rounded-xl bg-slate-900/60 border border-slate-800/80 hover:border-slate-700 transition">
          <div class="w-12 h-12 rounded-lg bg-slate-800 flex-shrink-0 overflow-hidden flex items-center justify-center border border-slate-700/60">
            ${item.thumbnail ? 
              `<img src="${item.thumbnail}" class="w-full h-full object-cover" onerror="this.onerror=null; this.parentElement.innerHTML='<i data-lucide=${icon} class=w-5 h-5 text-slate-400></i>'; if(window.lucide) window.lucide.createIcons();" />` :
              `<i data-lucide="${icon}" class="w-5 h-5 text-slate-400"></i>`
            }
          </div>
          <div class="flex-1 min-w-0">
            <h4 class="text-sm font-semibold text-slate-200 truncate" title="${item.title}">${item.title}</h4>
            <div class="flex items-center gap-2 mt-1 flex-wrap">
              <span class="text-[10px] font-medium uppercase px-2 py-0.5 rounded border ${badgeColor}">
                ${item.type.toUpperCase()} • ${item.quality}
              </span>
              <span class="text-xs text-slate-400 font-mono">${this.formatBytes(item.fileSize)}</span>
              <span class="text-[11px] text-slate-500">• ${this.formatDate(item.timestamp)}</span>
            </div>
          </div>
          ${item.downloadUrl ? `
            <a href="${item.downloadUrl}" download="${item.filename}" class="p-2 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/40 text-indigo-300 transition" title="Re-download">
              <i data-lucide="download" class="w-4 h-4"></i>
            </a>
          ` : ''}
        </div>
      `;
    }).join("");

    if (window.lucide) window.lucide.createIcons();
  }
};

window.HistoryManager = HistoryManager;
