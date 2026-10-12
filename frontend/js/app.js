document.addEventListener("DOMContentLoaded", () => {
  // Application State
  const state = {
    currentPlatform: "universal",
    activeUrl: "",
    activeData: null,
    isFetching: false,
    isDownloading: false,
    selectedMode: "all" // all, video, audio, image
  };

  // Platform definitions and metadata
  const platformConfigs = {
    universal: {
      name: "Universal Downloader",
      badge: "All-in-One Engine",
      colorClass: "accent-universal",
      placeholder: "Paste any link from YouTube, Instagram, TikTok, Reddit, X, Facebook, Threads...",
      heroTitle: "Universal Media & MP3 Downloader",
      heroSubtitle: "Download ultra-HD videos, crisp images, and high-fidelity 320kbps MP3 audio from any social platform with one click.",
      example: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
      guide: "Paste any supported social link. Our intelligent engine automatically detects the platform, parses all available video resolutions, extracts MP3 audio streams, and fetches image galleries."
    },
    youtube: {
      name: "YouTube",
      badge: "Videos, Shorts & MP3",
      colorClass: "accent-youtube",
      placeholder: "Paste YouTube Video or Shorts URL (e.g. https://www.youtube.com/watch?v=...)",
      heroTitle: "YouTube Video & MP3 Audio Downloader",
      heroSubtitle: "Save YouTube videos up to 1080p Full HD / 4K or extract pure 320kbps MP3 audio with zero quality loss.",
      example: "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
      guide: "Paste any YouTube video or Shorts URL. Select your preferred resolution (1080p, 720p, 480p) or click 'Download MP3' to convert it into high-fidelity audio."
    },
    instagram: {
      name: "Instagram",
      badge: "Reels, Posts & Stories",
      colorClass: "accent-instagram",
      placeholder: "Paste Instagram Reel, Video or Post link (e.g. https://www.instagram.com/reel/...)",
      heroTitle: "Instagram Reels, Photos & Audio Downloader",
      heroSubtitle: "Download Instagram Reels, Carousel photo albums, Stories, and background MP3 music tracks easily.",
      example: "https://www.instagram.com/reel/C3bA-xLpExample",
      guide: "Supports single reels, carousel galleries with multiple photos and videos, and audio extraction. Ensure the Instagram post is from a public profile."
    },
    facebook: {
      name: "Facebook",
      badge: "Reels & Watch",
      colorClass: "accent-facebook",
      placeholder: "Paste Facebook Video or Reel URL (e.g. https://www.facebook.com/watch/?v=...)",
      heroTitle: "Facebook Video & Audio Downloader",
      heroSubtitle: "Download Facebook Watch HD videos, viral reels, public page clips, and convert to MP3 audio files.",
      example: "https://www.facebook.com/watch/?v=10158432109876543",
      guide: "Copy the link of any public Facebook video or Reel. Paste here to download in HD MP4 or extract the soundtrack as MP3."
    },
    reddit: {
      name: "Reddit",
      badge: "Videos with Sound & Galleries",
      colorClass: "accent-reddit",
      placeholder: "Paste Reddit post URL (e.g. https://www.reddit.com/r/.../comments/...)",
      heroTitle: "Reddit Video with Audio & Image Gallery Downloader",
      heroSubtitle: "Overcome Reddit's separated video/audio streams: download fully merged MP4 videos with pristine sound, full galleries, and GIFs.",
      example: "https://www.reddit.com/r/NatureIsFuckingLit/comments/...",
      guide: "Reddit separates its video and audio streams natively. OmniStream automatically merges both with FFmpeg so your downloaded video has crystal-clear audio."
    },
    x: {
      name: "X / Twitter",
      badge: "Videos, GIFs & High-Res Photos",
      colorClass: "accent-x",
      placeholder: "Paste X / Twitter post URL (e.g. https://x.com/user/status/...)",
      heroTitle: "X / Twitter Video & GIF Downloader",
      heroSubtitle: "Download videos from X (Twitter) in highest available bitrate, animated GIFs as MP4, high-res photos, and audio.",
      example: "https://x.com/NASA/status/1757829871146811456",
      guide: "Supports both twitter.com and x.com URLs. Download single or multi-resolution videos, loopable GIFs, and attached media photos."
    },
    tiktok: {
      name: "TikTok",
      badge: "HD No Watermark & Sound",
      colorClass: "accent-tiktok",
      placeholder: "Paste TikTok video link (e.g. https://www.tiktok.com/@user/video/...)",
      heroTitle: "TikTok Video & MP3 Sound Downloader",
      heroSubtitle: "Download TikTok videos without watermark in crisp HD quality, and save original background sounds as MP3.",
      example: "https://www.tiktok.com/@tiktok/video/7123456789012345678",
      guide: "Paste any TikTok video or photo slideshow link. Download watermark-free HD MP4 or grab the viral audio as an MP3 track."
    },
    threads: {
      name: "Threads",
      badge: "Videos, Photos & Carousels",
      colorClass: "accent-threads",
      placeholder: "Paste Threads post link (e.g. https://www.threads.net/@user/post/...)",
      heroTitle: "Threads Video & Photo Downloader",
      heroSubtitle: "Save full HD videos, multi-image carousel posts, and audio clips directly from Meta Threads.",
      example: "https://www.threads.net/@zuck/post/CxExamplePost",
      guide: "Paste the URL of any public Threads post. OmniStream detects whether it contains a video stream, audio track, or high-res photos."
    }
  };

  // DOM Elements
  const urlInput = document.getElementById("url-input");
  const fetchBtn = document.getElementById("fetch-btn");
  const pasteBtn = document.getElementById("paste-btn");
  const clearBtn = document.getElementById("clear-btn");
  const sampleBtn = document.getElementById("sample-btn");
  const heroTitle = document.getElementById("hero-title");
  const heroSubtitle = document.getElementById("hero-subtitle");
  const heroBadge = document.getElementById("hero-badge");
  const platformTabs = document.querySelectorAll(".platform-tab");
  const quickCards = document.querySelectorAll(".quick-platform-card");
  const resultsContainer = document.getElementById("results-container");
  const errorContainer = document.getElementById("error-container");
  const errorMessage = document.getElementById("error-message");
  const loadingIndicator = document.getElementById("loading-indicator");
  const guideText = document.getElementById("guide-text");

  // History Drawer Elements
  const historyDrawer = document.getElementById("history-drawer");
  const openHistoryBtn = document.getElementById("open-history-btn");
  const closeHistoryBtn = document.getElementById("close-history-btn");
  const clearHistoryBtn = document.getElementById("clear-history-btn");

  // Format filter switches
  const filterPills = document.querySelectorAll(".filter-pill");

  // Initialize Icons & History
  if (window.lucide) window.lucide.createIcons();
  if (window.HistoryManager) {
    window.HistoryManager.updateBadge();
    window.HistoryManager.render();
  }

  // Switch Platform Section
  function switchPlatform(platformId) {
    if (!platformConfigs[platformId]) platformId = "universal";
    state.currentPlatform = platformId;
    const config = platformConfigs[platformId];

    // Update active tab styles
    platformTabs.forEach(tab => {
      const p = tab.getAttribute("data-platform");
      if (p === platformId) {
        tab.classList.add("bg-indigo-600", "text-white", "shadow-lg", "shadow-indigo-500/25");
        tab.classList.remove("text-slate-400", "hover:text-slate-200", "bg-transparent");
      } else {
        tab.classList.remove("bg-indigo-600", "text-white", "shadow-lg", "shadow-indigo-500/25");
        tab.classList.add("text-slate-400", "hover:text-slate-200", "bg-transparent");
      }
    });

    // Update quick cards
    quickCards.forEach(card => {
      const p = card.getAttribute("data-platform");
      if (p === platformId) {
        card.classList.add("border-indigo-500", "bg-indigo-950/30");
      } else {
        card.classList.remove("border-indigo-500", "bg-indigo-950/30");
      }
    });

    // Update Hero elements
    heroTitle.textContent = config.heroTitle;
    heroSubtitle.textContent = config.heroSubtitle;
    heroBadge.textContent = config.badge;
    urlInput.placeholder = config.placeholder;
    if (guideText) guideText.textContent = config.guide;

    // Reset results on platform switch if input is empty
    if (!urlInput.value.trim()) {
      hideResults();
      hideError();
    }
  }

  // Event Listeners for Platform Tabs
  platformTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      const p = tab.getAttribute("data-platform");
      switchPlatform(p);
    });
  });

  quickCards.forEach(card => {
    card.addEventListener("click", () => {
      const p = card.getAttribute("data-platform");
      switchPlatform(p);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  });

  // Filter Pills (All / Video / Audio / Image)
  filterPills.forEach(pill => {
    pill.addEventListener("click", () => {
      filterPills.forEach(p => {
        p.classList.remove("bg-indigo-600/30", "border-indigo-500", "text-indigo-300");
        p.classList.add("text-slate-400", "border-slate-800");
      });
      pill.classList.add("bg-indigo-600/30", "border-indigo-500", "text-indigo-300");
      pill.classList.remove("text-slate-400", "border-slate-800");
      state.selectedMode = pill.getAttribute("data-mode");
      if (state.activeData) {
        renderResults(state.activeData);
      }
    });
  });

  // Paste from clipboard
  pasteBtn.addEventListener("click", async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) {
        urlInput.value = text.trim();
        handleFetch();
      }
    } catch (e) {
      alert("Please paste the link directly into the text box (Ctrl+V).");
    }
  });

  // Clear input
  clearBtn.addEventListener("click", () => {
    urlInput.value = "";
    hideResults();
    hideError();
    urlInput.focus();
  });

  // Sample URL loader
  sampleBtn.addEventListener("click", () => {
    const config = platformConfigs[state.currentPlatform] || platformConfigs.universal;
    urlInput.value = config.example;
    handleFetch();
  });

  // Input Enter key
  urlInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleFetch();
    }
  });

  fetchBtn.addEventListener("click", handleFetch);

  // Fetch Media Handler
  async function handleFetch() {
    const url = urlInput.value.trim();
    if (!url) {
      showError("Please enter or paste a valid link.");
      return;
    }

    hideError();
    hideResults();
    setLoading(true);

    try {
      const data = await window.DownloaderAPI.fetchInfo(url, state.currentPlatform);
      state.activeData = data;
      state.activeUrl = url;

      // Auto-switch platform tab if universal detected a specific platform
      if (data.platform && platformConfigs[data.platform] && state.currentPlatform === "universal") {
        const detectedConfig = platformConfigs[data.platform];
        heroBadge.textContent = `Auto-Detected: ${detectedConfig.name}`;
      }

      renderResults(data);
    } catch (err) {
      showError(err.message || "Failed to fetch media. Please check the URL.");
    } finally {
      setLoading(false);
    }
  }

  // Render Result Cards
  function renderResults(data) {
    if (!data) return;
    resultsContainer.classList.remove("hidden");

    const isVideo = data.is_video;
    const isCarousel = data.media_type === "carousel" || data.media_type === "gallery";
    const formats = data.formats || [];

    // Separate video formats and audio formats
    const videoFormats = formats.filter(f => f.type === "video");
    const audioFormats = formats.filter(f => f.type === "audio");

    let mediaPreviewHtml = "";
    if (data.thumbnail) {
      mediaPreviewHtml = `
        <div class="relative w-full rounded-2xl overflow-hidden bg-slate-950 aspect-video flex items-center justify-center border border-slate-800 shadow-xl group">
          <img src="${data.thumbnail}" class="w-full h-full object-contain" alt="Media thumbnail" />
          ${isVideo ? `
            <div class="absolute inset-0 bg-black/40 flex items-center justify-center backdrop-blur-[2px]">
              <div class="w-16 h-16 rounded-full bg-indigo-600/90 text-white flex items-center justify-center shadow-lg transform group-hover:scale-110 transition">
                <i data-lucide="play" class="w-8 h-8 ml-1"></i>
              </div>
            </div>
          ` : ''}
          ${data.duration ? `
            <span class="absolute bottom-3 right-3 bg-black/80 backdrop-blur-md text-white text-xs px-2.5 py-1 rounded-md font-mono border border-white/10 font-semibold">
              ${formatDuration(data.duration)}
            </span>
          ` : ''}
        </div>
      `;
    }

    // Video Options HTML
    let videoSectionHtml = "";
    if (isVideo && videoFormats.length > 0 && (state.selectedMode === "all" || state.selectedMode === "video")) {
      videoSectionHtml = `
        <div class="p-5 rounded-2xl bg-slate-900/80 border border-slate-800/90 mb-5">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-2">
              <div class="p-2 rounded-lg bg-blue-500/10 text-blue-400">
                <i data-lucide="video" class="w-5 h-5"></i>
              </div>
              <div>
                <h4 class="font-bold text-slate-100 text-base">Video Downloads</h4>
                <p class="text-xs text-slate-400">Choose your desired MP4 resolution</p>
              </div>
            </div>
            <span class="text-xs font-semibold px-2.5 py-1 rounded-full bg-blue-500/10 text-blue-300 border border-blue-500/20">
              MP4 Format
            </span>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            ${videoFormats.map(fmt => `
              <button 
                class="download-btn group flex items-center justify-between p-3.5 rounded-xl bg-slate-800/60 hover:bg-indigo-600 border border-slate-700/60 hover:border-indigo-500 text-left transition transform hover:-translate-y-0.5 active:translate-y-0"
                data-type="video"
                data-quality="${fmt.quality || fmt.id}"
                data-title="${escapeHtml(data.title)}"
              >
                <div>
                  <div class="font-bold text-slate-200 group-hover:text-white text-sm flex items-center gap-1.5">
                    ${fmt.label}
                    ${fmt.recommended ? `<span class="text-[10px] bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 px-1.5 py-0.5 rounded">FAST</span>` : ''}
                  </div>
                  <span class="text-[11px] text-slate-400 group-hover:text-indigo-100 font-mono">High Quality Stream</span>
                </div>
                <div class="p-2 rounded-lg bg-slate-700/50 group-hover:bg-white/20 text-slate-300 group-hover:text-white transition">
                  <i data-lucide="download" class="w-4 h-4"></i>
                </div>
              </button>
            `).join("")}
          </div>
        </div>
      `;
    }

    // Audio / MP3 Section HTML
    let audioSectionHtml = "";
    if (isVideo && (state.selectedMode === "all" || state.selectedMode === "audio")) {
      audioSectionHtml = `
        <div class="p-5 rounded-2xl bg-gradient-to-br from-fuchsia-950/20 via-slate-900/90 to-purple-950/20 border border-fuchsia-500/30 mb-5 relative overflow-hidden">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-3">
              <div class="p-2.5 rounded-xl bg-fuchsia-500/20 text-fuchsia-400 border border-fuchsia-500/30 shadow-inner">
                <i data-lucide="music" class="w-6 h-6"></i>
              </div>
              <div>
                <div class="flex items-center gap-2">
                  <h4 class="font-extrabold text-slate-100 text-lg">Extract Pure MP3 Audio</h4>
                  <div class="flex items-center gap-1">
                    <div class="soundwave-bar"></div>
                    <div class="soundwave-bar"></div>
                    <div class="soundwave-bar"></div>
                    <div class="soundwave-bar"></div>
                    <div class="soundwave-bar"></div>
                  </div>
                </div>
                <p class="text-xs text-slate-400">Convert this video into high-fidelity standalone MP3 audio with FFmpeg</p>
              </div>
            </div>
            <span class="text-xs font-bold px-3 py-1 rounded-full bg-fuchsia-500/20 text-fuchsia-300 border border-fuchsia-500/40 uppercase tracking-wider">
              Only MP3
            </span>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
            <button 
              class="download-btn group flex items-center justify-between p-4 rounded-xl bg-fuchsia-950/40 hover:bg-fuchsia-600 border border-fuchsia-500/40 hover:border-fuchsia-400 text-left transition transform hover:-translate-y-0.5 active:translate-y-0 shadow-lg shadow-fuchsia-950/30"
              data-type="audio"
              data-quality="mp3_320"
              data-title="${escapeHtml(data.title)}"
            >
              <div>
                <div class="font-extrabold text-slate-100 group-hover:text-white text-base flex items-center gap-2">
                  Download MP3 (320 kbps)
                  <span class="text-[10px] bg-emerald-500/30 text-emerald-200 border border-emerald-400/40 px-2 py-0.5 rounded-full font-bold">HQ</span>
                </div>
                <span class="text-xs text-fuchsia-300/80 group-hover:text-fuchsia-100">Crystal Clear Studio Bitrate</span>
              </div>
              <div class="p-2.5 rounded-xl bg-fuchsia-800/40 group-hover:bg-white text-white group-hover:text-fuchsia-700 transition">
                <i data-lucide="headphones" class="w-5 h-5"></i>
              </div>
            </button>

            <button 
              class="download-btn group flex items-center justify-between p-4 rounded-xl bg-purple-950/40 hover:bg-purple-600 border border-purple-500/40 hover:border-purple-400 text-left transition transform hover:-translate-y-0.5 active:translate-y-0 shadow-lg shadow-purple-950/30"
              data-type="audio"
              data-quality="mp3_192"
              data-title="${escapeHtml(data.title)}"
            >
              <div>
                <div class="font-bold text-slate-100 group-hover:text-white text-base flex items-center gap-2">
                  Download MP3 (192 kbps)
                  <span class="text-[10px] bg-slate-700 text-slate-300 px-2 py-0.5 rounded-full font-medium">Standard</span>
                </div>
                <span class="text-xs text-purple-300/80 group-hover:text-purple-100">Fast Download & Smaller Size</span>
              </div>
              <div class="p-2.5 rounded-xl bg-purple-800/40 group-hover:bg-white text-white group-hover:text-purple-700 transition">
                <i data-lucide="music-2" class="w-5 h-5"></i>
              </div>
            </button>
          </div>
        </div>
      `;
    }

    // Images / Gallery / Carousel HTML
    let imageSectionHtml = "";
    const hasMultipleItems = data.items && data.items.length > 1;
    const isSingleImage = !isVideo || (data.media_type === "image");

    if (hasMultipleItems && (state.selectedMode === "all" || state.selectedMode === "image")) {
      imageSectionHtml = `
        <div class="p-5 rounded-2xl bg-slate-900/80 border border-slate-800/90 mb-5">
          <div class="flex items-center justify-between mb-4 flex-wrap gap-2">
            <div class="flex items-center gap-2">
              <div class="p-2 rounded-lg bg-amber-500/10 text-amber-400">
                <i data-lucide="images" class="w-5 h-5"></i>
              </div>
              <div>
                <h4 class="font-bold text-slate-100 text-base">Media Gallery (${data.items.length} Items)</h4>
                <p class="text-xs text-slate-400">Full resolution photos & carousel slides</p>
              </div>
            </div>
            <button id="download-all-btn" class="px-3.5 py-1.5 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-bold text-xs flex items-center gap-1.5 shadow transition">
              <i data-lucide="download-cloud" class="w-4 h-4"></i>
              Download All (${data.items.length})
            </button>
          </div>

          <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            ${data.items.map((item, idx) => `
              <div class="relative group rounded-xl overflow-hidden bg-slate-800 border border-slate-700/80 aspect-square">
                <img src="${item.url || item.thumbnail}" class="w-full h-full object-cover" alt="Gallery item" loading="lazy" />
                <div class="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition flex flex-col items-center justify-center p-2 text-center gap-2 backdrop-blur-[2px]">
                  <span class="text-xs text-white font-medium">Slide #${idx + 1}</span>
                  <button 
                    class="download-btn px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center gap-1.5 shadow"
                    data-type="${item.type || 'image'}"
                    data-item-index="${idx}"
                    data-title="${escapeHtml(data.title)}_${idx + 1}"
                  >
                    <i data-lucide="download" class="w-3.5 h-3.5"></i>
                    Download
                  </button>
                </div>
              </div>
            `).join("")}
          </div>
        </div>
      `;
    } else if (isSingleImage && (state.selectedMode === "all" || state.selectedMode === "image")) {
      const imgUrl = (data.items && data.items[0]) ? data.items[0].url : data.thumbnail;
      imageSectionHtml = `
        <div class="p-5 rounded-2xl bg-gradient-to-br from-amber-950/20 via-slate-900/90 to-orange-950/20 border border-amber-500/30 mb-5">
          <div class="flex items-center justify-between mb-4 flex-wrap gap-3">
            <div class="flex items-center gap-3">
              <div class="p-2.5 rounded-xl bg-amber-500/20 text-amber-400 border border-amber-500/30">
                <i data-lucide="image" class="w-6 h-6"></i>
              </div>
              <div>
                <h4 class="font-extrabold text-slate-100 text-lg">High-Resolution Photo</h4>
                <p class="text-xs text-slate-400">Download the original full quality image</p>
              </div>
            </div>
            <button 
              class="download-btn px-5 py-2.5 rounded-xl bg-amber-600 hover:bg-amber-500 text-white font-extrabold text-sm flex items-center gap-2 shadow-lg shadow-amber-950/50 transition transform hover:-translate-y-0.5 active:translate-y-0"
              data-type="image"
              data-item-index="0"
              data-title="${escapeHtml(data.title)}"
            >
              <i data-lucide="download" class="w-4 h-4"></i>
              Download Full Image
            </button>
          </div>
        </div>
      `;
    }

    // Assemble final container HTML
    resultsContainer.innerHTML = `
      <div class="glass-panel p-6 sm:p-8 rounded-3xl animate-fadeIn">
        <!-- Media Header Info -->
        <div class="flex flex-col md:flex-row gap-6 mb-6 pb-6 border-b border-slate-800">
          <div class="w-full md:w-72 flex-shrink-0">
            ${mediaPreviewHtml}
          </div>
          <div class="flex-1 flex flex-col justify-between">
            <div>
              <div class="flex items-center gap-2 mb-2 flex-wrap">
                <span class="text-xs font-bold uppercase px-2.5 py-1 rounded-md bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 flex items-center gap-1.5">
                  <i data-lucide="globe" class="w-3.5 h-3.5"></i>
                  ${data.platform.toUpperCase()}
                </span>
                <span class="text-xs font-semibold px-2.5 py-1 rounded-md bg-slate-800 text-slate-300 border border-slate-700/60">
                  ${data.media_type.toUpperCase()}
                </span>
              </div>
              <h3 class="text-xl sm:text-2xl font-extrabold text-white leading-snug mb-3">
                ${data.title}
              </h3>
              ${data.author ? `
                <div class="flex items-center gap-2 text-sm text-slate-400 font-medium mb-3">
                  <i data-lucide="user" class="w-4 h-4 text-indigo-400"></i>
                  <span>${data.author}</span>
                </div>
              ` : ''}
            </div>

            <!-- Action shortcuts -->
            <div class="flex items-center gap-2 pt-2 flex-wrap">
              <button id="copy-link-btn" class="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-2 border border-slate-700 transition">
                <i data-lucide="copy" class="w-3.5 h-3.5"></i>
                Copy Source Link
              </button>
            </div>
          </div>
        </div>

        <!-- Download Action Sections -->
        ${audioSectionHtml}
        ${videoSectionHtml}
        ${imageSectionHtml}

        <!-- Download Progress Toast Modal / Banner -->
        <div id="download-progress-banner" class="hidden mt-4 p-4 rounded-xl bg-indigo-950/80 border border-indigo-500/50 flex items-center gap-3">
          <div class="w-5 h-5 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin flex-shrink-0"></div>
          <div class="flex-1 min-w-0">
            <p id="download-progress-status" class="text-sm font-semibold text-indigo-200">Processing media stream...</p>
            <p class="text-xs text-indigo-300/70">Conversion in progress. Your download will start automatically.</p>
          </div>
        </div>
      </div>
    `;

    if (window.lucide) window.lucide.createIcons();

    // Attach Download Button Listeners
    const dlButtons = resultsContainer.querySelectorAll(".download-btn");
    dlButtons.forEach(btn => {
      btn.addEventListener("click", () => {
        const type = btn.getAttribute("data-type") || "video";
        const quality = btn.getAttribute("data-quality") || "best";
        const title = btn.getAttribute("data-title") || data.title;
        const itemIdx = btn.getAttribute("data-item-index");
        let imageUrl = null;
        if (itemIdx !== null && data.items && data.items[parseInt(itemIdx)]) {
          imageUrl = data.items[parseInt(itemIdx)].url;
        } else {
          imageUrl = btn.getAttribute("data-image-url") || (data.thumbnail || null);
        }
        triggerFileDownload({ type, quality, title, imageUrl });
      });
    });

    // Batch download all carousel items
    const downloadAllBtn = document.getElementById("download-all-btn");
    if (downloadAllBtn && data.items) {
      downloadAllBtn.addEventListener("click", async () => {
        for (let i = 0; i < data.items.length; i++) {
          const itm = data.items[i];
          await triggerFileDownload({
            type: itm.type || "image",
            quality: "best",
            title: `${data.title}_${i + 1}`,
            imageUrl: itm.url
          });
          // Small delay between batch downloads
          await new Promise(r => setTimeout(r, 800));
        }
      });
    }

    // Copy source link listener
    const copyLinkBtn = document.getElementById("copy-link-btn");
    if (copyLinkBtn) {
      copyLinkBtn.addEventListener("click", () => {
        navigator.clipboard.writeText(state.activeUrl);
        copyLinkBtn.innerHTML = `<i data-lucide="check" class="w-3.5 h-3.5 text-emerald-400"></i> Copied!`;
        if (window.lucide) window.lucide.createIcons();
        setTimeout(() => {
          copyLinkBtn.innerHTML = `<i data-lucide="copy" class="w-3.5 h-3.5"></i> Copy Source Link`;
          if (window.lucide) window.lucide.createIcons();
        }, 2000);
      });
    }
  }

  // Handle Download Request
  async function triggerFileDownload({ type, quality, title, imageUrl }) {
    if (state.isDownloading) return;
    state.isDownloading = true;

    const banner = document.getElementById("download-progress-banner");
    const statusText = document.getElementById("download-progress-status");
    if (banner) banner.classList.remove("hidden");

    try {
      await window.DownloaderAPI.startDownload({
        url: state.activeUrl,
        type: type,
        quality: quality,
        title: title,
        imageUrl: imageUrl
      }, (msg) => {
        if (statusText) statusText.textContent = msg;
      });

      if (statusText) statusText.textContent = "Download completed! Check your downloads.";
      setTimeout(() => {
        if (banner) banner.classList.add("hidden");
      }, 3000);
    } catch (err) {
      alert("Download error: " + (err.message || "Could not process media stream."));
      if (banner) banner.classList.add("hidden");
    } finally {
      state.isDownloading = false;
    }
  }

  // Helpers
  function setLoading(isLoading) {
    state.isFetching = isLoading;
    if (isLoading) {
      loadingIndicator.classList.remove("hidden");
      fetchBtn.disabled = true;
      fetchBtn.classList.add("opacity-60", "cursor-not-allowed");
    } else {
      loadingIndicator.classList.add("hidden");
      fetchBtn.disabled = false;
      fetchBtn.classList.remove("opacity-60", "cursor-not-allowed");
    }
  }

  function showError(msg) {
    errorMessage.textContent = msg;
    errorContainer.classList.remove("hidden");
    resultsContainer.classList.add("hidden");
  }

  function hideError() {
    errorContainer.classList.add("hidden");
  }

  function hideResults() {
    resultsContainer.classList.add("hidden");
  }

  function formatDuration(sec) {
    if (!sec) return "";
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  }

  function escapeHtml(str) {
    if (!str) return "";
    return str.replace(/[&<>"']/g, function(m) {
      return ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
      })[m];
    });
  }

  // History Drawer Controls
  if (openHistoryBtn && historyDrawer) {
    openHistoryBtn.addEventListener("click", () => {
      historyDrawer.classList.remove("translate-x-full");
      if (window.HistoryManager) window.HistoryManager.render();
    });
  }

  if (closeHistoryBtn && historyDrawer) {
    closeHistoryBtn.addEventListener("click", () => {
      historyDrawer.classList.add("translate-x-full");
    });
  }

  if (clearHistoryBtn) {
    clearHistoryBtn.addEventListener("click", () => {
      if (confirm("Are you sure you want to clear your download history?")) {
        if (window.HistoryManager) window.HistoryManager.clearHistory();
      }
    });
  }

  // Check backend health on boot
  fetch("/api/health")
    .then(r => r.json())
    .then(data => {
      const statusDot = document.getElementById("server-status-dot");
      const statusText = document.getElementById("server-status-text");
      if (statusDot && data.status === "healthy") {
        statusDot.classList.remove("bg-slate-500");
        statusDot.classList.add("bg-emerald-400");
        if (statusText) statusText.textContent = "Online • FFmpeg Ready";
      }
    })
    .catch(() => {
      const statusDot = document.getElementById("server-status-dot");
      const statusText = document.getElementById("server-status-text");
      if (statusDot) {
        statusDot.classList.remove("bg-slate-500");
        statusDot.classList.add("bg-amber-400");
        if (statusText) statusText.textContent = "Backend connecting...";
      }
    });
});
