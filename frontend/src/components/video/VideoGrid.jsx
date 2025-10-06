import React from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  ChevronLeft, 
  ChevronRight, 
  Clock, 
  User, 
  Calendar,
  Play
} from 'lucide-react';
import { videosAPI } from '../../lib/api';

const VideoCard = ({ video }) => {
  const formatDuration = (seconds) => {
    if (!seconds) return '';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '';
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
  };

  return (
    <Card className="group overflow-hidden hover:shadow-lg transition-all duration-200">
      <div className="relative aspect-video bg-muted">
        {/* Thumbnail */}
        {video.thumbnail_url ? (
          <img
            src={videosAPI.getThumbnailUrl(video.id)}
            alt={video.title}
            className="w-full h-full object-cover"
            onError={(e) => {
              e.target.style.display = 'none';
            }}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-muted">
            <Play className="h-12 w-12 text-muted-foreground" />
          </div>
        )}
        
        {/* Duration Badge */}
        {video.duration && (
          <Badge 
            variant="secondary" 
            className="absolute bottom-2 right-2 bg-black/70 text-white hover:bg-black/70"
          >
            <Clock className="h-3 w-3 mr-1" />
            {formatDuration(video.duration)}
          </Badge>
        )}

        {/* Processing Status */}
        {video.processing_status !== 'completed' && (
          <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
            <Badge variant={video.processing_status === 'failed' ? 'destructive' : 'secondary'}>
              {video.processing_status === 'processing' && `Processing ${video.processing_progress}%`}
              {video.processing_status === 'pending' && 'Processing...'}
              {video.processing_status === 'failed' && 'Processing Failed'}
            </Badge>
          </div>
        )}

        {/* Hover Overlay */}
        <Link 
          to={`/video/${video.id}`}
          className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors duration-200 flex items-center justify-center"
        >
          <Play className="h-12 w-12 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
        </Link>
      </div>

      <CardContent className="p-4">
        <div className="space-y-2">
          {/* Title */}
          <Link to={`/video/${video.id}`}>
            <h3 className="font-semibold line-clamp-2 hover:text-primary transition-colors">
              {video.title}
            </h3>
          </Link>

          {/* Metadata */}
          <div className="flex items-center text-sm text-muted-foreground space-x-4">
            <div className="flex items-center">
              <User className="h-3 w-3 mr-1" />
              <span>{video.uploader_username}</span>
            </div>
            <div className="flex items-center">
              <Calendar className="h-3 w-3 mr-1" />
              <span>{formatDate(video.uploaded_at)}</span>
            </div>
          </div>

          {/* Category */}
          {video.category_name && (
            <Badge variant="outline" className="text-xs">
              {video.category_name}
            </Badge>
          )}

          {/* Tags */}
          {video.tags && video.tags.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {video.tags.slice(0, 3).map((tag, index) => (
                <Badge key={index} variant="secondary" className="text-xs">
                  #{tag}
                </Badge>
              ))}
              {video.tags.length > 3 && (
                <Badge variant="secondary" className="text-xs">
                  +{video.tags.length - 3}
                </Badge>
              )}
            </div>
          )}

          {/* File Info */}
          <div className="text-xs text-muted-foreground">
            {video.width && video.height && (
              <span>{video.width}×{video.height}</span>
            )}
            {video.file_size && (
              <span className="ml-2">{formatFileSize(video.file_size)}</span>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

const VideoGrid = ({ videos, pagination, onPageChange, loading }) => {
  if (!videos || videos.length === 0) {
    return null;
  }

  return (
    <div className="space-y-6">
      {/* Videos Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {videos.map((video) => (
          <VideoCard key={video.id} video={video} />
        ))}
      </div>

      {/* Pagination */}
      {pagination && pagination.pages > 1 && (
        <div className="flex items-center justify-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(pagination.page - 1)}
            disabled={!pagination.has_prev || loading}
          >
            <ChevronLeft className="h-4 w-4" />
            Previous
          </Button>

          <div className="flex items-center space-x-1">
            {Array.from({ length: Math.min(5, pagination.pages) }, (_, i) => {
              let pageNum;
              if (pagination.pages <= 5) {
                pageNum = i + 1;
              } else if (pagination.page <= 3) {
                pageNum = i + 1;
              } else if (pagination.page >= pagination.pages - 2) {
                pageNum = pagination.pages - 4 + i;
              } else {
                pageNum = pagination.page - 2 + i;
              }

              return (
                <Button
                  key={pageNum}
                  variant={pageNum === pagination.page ? "default" : "outline"}
                  size="sm"
                  onClick={() => onPageChange(pageNum)}
                  disabled={loading}
                >
                  {pageNum}
                </Button>
              );
            })}
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(pagination.page + 1)}
            disabled={!pagination.has_next || loading}
          >
            Next
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      )}

      {/* Results Info */}
      {pagination && (
        <div className="text-center text-sm text-muted-foreground">
          Showing {((pagination.page - 1) * pagination.per_page) + 1} to{' '}
          {Math.min(pagination.page * pagination.per_page, pagination.total)} of{' '}
          {pagination.total} videos
        </div>
      )}
    </div>
  );
};

export default VideoGrid;
