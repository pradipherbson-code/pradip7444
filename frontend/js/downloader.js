const DownloaderAPI = {
  activeMediaData: null,

  async fetchInfo(url, platform = null) {
    if (!url || !url.trim()) {
      throw new Error("Please enter a valid link.");
    }

    const payload = {
      url: url.trim(),
      platform: platform && platform !== "universal" ? platform : null
    };

    const response = await fetch("/api/fetch-info", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await response.json();
    if (!response.ok || !data.success) {
      throw new Error(data.error || "Failed to fetch media details.");
    }

    this.activeMediaData = data;
    return data;
  },

  async startDownload({ url, type = "video", quality = "best", title = null, imageUrl = null }, onProgress = null) {
    if (onProgress) onProgress("Preparing download and processing stream...");

    const payload = {
      url: url || "",
      type: type,
      quality: quality,
      title: title || (this.activeMediaData ? this.activeMediaData.title : "media"),
      image_url: imageUrl || null
    };

    const response = await fetch("/api/download", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await response.json();
    if (!response.ok || !data.success) {
      throw new Error(data.error || "Download conversion failed. Please try another quality option.");
    }

    if (onProgress) onProgress("Conversion ready! Initiating browser download...");

    // Record to history
    if (window.HistoryManager) {
      window.HistoryManager.addItem({
        title: data.filename || payload.title,
        platform: this.activeMediaData ? this.activeMediaData.platform : "universal",
        type: data.type || type,
        quality: quality,
        filename: data.filename,
        fileSize: data.size,
        thumbnail: this.activeMediaData ? this.activeMediaData.thumbnail : "",
        downloadUrl: data.download_url
      });
    }

    // Trigger native browser download via invisible anchor tag
    const link = document.createElement("a");
    link.href = data.download_url;
    link.download = data.filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    return data;
  }
};

window.DownloaderAPI = DownloaderAPI;
