import React, { useEffect, useRef } from 'react';
import videojs from 'video.js';
import 'video.js/dist/video-js.css';
import '@videojs/themes/dist/city/index.css';
import { videosAPI } from '../../lib/api';

const VideoPlayer = ({ video, options = {} }) => {
  const videoRef = useRef(null);
  const playerRef = useRef(null);

  useEffect(() => {
    // Make sure Video.js player is only initialized once
    if (!playerRef.current) {
      const videoElement = videoRef.current;

      if (!videoElement) return;

      // Create sources array with different resolutions
      const sources = [];
      
      // Add original quality
      sources.push({
        src: videosAPI.getStreamUrl(video.id, 'original'),
        type: 'video/mp4',
        label: 'Original',
        res: video.height || 1080
      });

      // Add processed resolutions
      if (video.resolutions) {
        video.resolutions.forEach(resolution => {
          sources.push({
            src: videosAPI.getStreamUrl(video.id, resolution.resolution),
            type: 'video/mp4',
            label: resolution.resolution,
            res: resolution.height
          });
        });
      }

      // Sort sources by resolution (highest first)
      sources.sort((a, b) => b.res - a.res);

      const playerOptions = {
        controls: true,
        responsive: true,
        fluid: true,
        playbackRates: [0.5, 1, 1.25, 1.5, 2],
        preload: 'metadata',
        poster: video.thumbnail_url ? videosAPI.getThumbnailUrl(video.id) : undefined,
        sources: sources,
        html5: {
          vhs: {
            overrideNative: true
          }
        },
        ...options
      };

      playerRef.current = videojs(videoElement, playerOptions, () => {
        console.log('Video.js player is ready');
      });

      // Add quality selector if multiple sources
      if (sources.length > 1) {
        playerRef.current.ready(() => {
          // Quality selector plugin would go here
          // For now, we'll use the built-in source selection
        });
      }
    }

    // Cleanup function
    return () => {
      if (playerRef.current && !playerRef.current.isDisposed()) {
        playerRef.current.dispose();
        playerRef.current = null;
      }
    };
  }, [video, options]);

  return (
    <div className="video-player-container">
      <div data-vjs-player>
        <video
          ref={videoRef}
          className="video-js vjs-theme-city vjs-big-play-centered"
          playsInline
        />
      </div>
    </div>
  );
};

export default VideoPlayer;
