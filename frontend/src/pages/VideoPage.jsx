import React, { useEffect, useRef } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../contexts/AuthContext';
import { videosAPI } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { 
  Download, 
  Edit, 
  Trash2, 
  User, 
  Calendar, 
  Clock, 
  HardDrive,
  MoreVertical,
  Play,
  ArrowLeft
} from 'lucide-react';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import VideoPlayer from '../components/video/VideoPlayer';
import { useToast } from '@/hooks/use-toast';

const VideoPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const { toast } = useToast();
  const queryClient = useQueryClient();

  // Fetch video data
  const {
    data: videoData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['video', id],
    queryFn: () => videosAPI.getVideo(id),
    enabled: !!id,
  });

  // Delete video mutation
  const deleteVideoMutation = useMutation({
    mutationFn: () => videosAPI.deleteVideo(id),
    onSuccess: () => {
      toast({
        title: "Success",
        description: "Video deleted successfully",
      });
      queryClient.invalidateQueries(['videos']);
      navigate('/');
    },
    onError: (error) => {
      toast({
        title: "Error",
        description: error.response?.data?.error || "Failed to delete video",
        variant: "destructive",
      });
    },
  });

  const video = videoData?.data?.video;

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
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '';
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
  };

  const canModify = user && (user.role === 'admin' || user.id === video?.uploader_id);
  const canDownload = isAuthenticated;

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this video? This action cannot be undone.')) {
      deleteVideoMutation.mutate();
    }
  };

  const handleDownload = (resolution = 'original') => {
    const downloadUrl = videosAPI.getDownloadUrl(video.id, resolution);
    window.open(downloadUrl, '_blank');
  };

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4">
        <Alert variant="destructive">
          <AlertDescription>
            {error.response?.data?.error || 'Failed to load video'}
          </AlertDescription>
        </Alert>
        <Button onClick={() => navigate('/')} variant="outline">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Home
        </Button>
      </div>
    );
  }

  if (!video) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold mb-4">Video not found</h2>
        <Button onClick={() => navigate('/')} variant="outline">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Home
        </Button>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Back Button */}
      <Button onClick={() => navigate('/')} variant="outline" size="sm">
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back to Videos
      </Button>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Video Player */}
          <Card>
            <CardContent className="p-0">
              {video.processing_status === 'completed' ? (
                <VideoPlayer video={video} />
              ) : (
                <div className="aspect-video bg-muted flex items-center justify-center">
                  <div className="text-center">
                    <Play className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                    <div className="space-y-2">
                      <Badge variant={video.processing_status === 'failed' ? 'destructive' : 'secondary'}>
                        {video.processing_status === 'processing' && `Processing ${video.processing_progress}%`}
                        {video.processing_status === 'pending' && 'Processing...'}
                        {video.processing_status === 'failed' && 'Processing Failed'}
                      </Badge>
                      {video.processing_status === 'processing' && (
                        <div className="w-64 bg-secondary rounded-full h-2 mx-auto">
                          <div 
                            className="bg-primary h-2 rounded-full transition-all duration-300"
                            style={{ width: `${video.processing_progress}%` }}
                          />
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Video Info */}
          <Card>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="space-y-2">
                  <CardTitle className="text-2xl">{video.title}</CardTitle>
                  <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                    <div className="flex items-center">
                      <User className="h-4 w-4 mr-1" />
                      <Link 
                        to={`/?uploader_id=${video.uploader_id}`}
                        className="hover:text-primary"
                      >
                        {video.uploader_username}
                      </Link>
                    </div>
                    <div className="flex items-center">
                      <Calendar className="h-4 w-4 mr-1" />
                      <span>{formatDate(video.uploaded_at)}</span>
                    </div>
                    {video.duration && (
                      <div className="flex items-center">
                        <Clock className="h-4 w-4 mr-1" />
                        <span>{formatDuration(video.duration)}</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Action Menu */}
                {(canModify || canDownload) && (
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="outline" size="sm">
                        <MoreVertical className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      {canDownload && (
                        <DropdownMenuItem onClick={() => handleDownload()}>
                          <Download className="mr-2 h-4 w-4" />
                          Download Original
                        </DropdownMenuItem>
                      )}
                      {canDownload && video.resolutions && video.resolutions.length > 0 && (
                        <>
                          {video.resolutions.map((res) => (
                            <DropdownMenuItem 
                              key={res.id} 
                              onClick={() => handleDownload(res.resolution)}
                            >
                              <Download className="mr-2 h-4 w-4" />
                              Download {res.resolution}
                            </DropdownMenuItem>
                          ))}
                        </>
                      )}
                      {canModify && (
                        <>
                          <DropdownMenuItem onClick={() => navigate(`/video/${video.id}/edit`)}>
                            <Edit className="mr-2 h-4 w-4" />
                            Edit Video
                          </DropdownMenuItem>
                          <DropdownMenuItem 
                            onClick={handleDelete}
                            className="text-destructive"
                          >
                            <Trash2 className="mr-2 h-4 w-4" />
                            Delete Video
                          </DropdownMenuItem>
                        </>
                      )}
                    </DropdownMenuContent>
                  </DropdownMenu>
                )}
              </div>
            </CardHeader>
            
            {video.description && (
              <CardContent>
                <div className="prose prose-sm max-w-none">
                  <p className="whitespace-pre-wrap">{video.description}</p>
                </div>
              </CardContent>
            )}
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Video Details */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Video Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Category */}
              {video.category_name && (
                <div>
                  <h4 className="font-medium mb-1">Category</h4>
                  <Link to={`/?category_id=${video.category_id}`}>
                    <Badge variant="outline" className="hover:bg-accent">
                      {video.category_name}
                    </Badge>
                  </Link>
                </div>
              )}

              {/* Tags */}
              {video.tags && video.tags.length > 0 && (
                <div>
                  <h4 className="font-medium mb-2">Tags</h4>
                  <div className="flex flex-wrap gap-1">
                    {video.tags.map((tag, index) => (
                      <Badge key={index} variant="secondary" className="text-xs">
                        #{tag}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Technical Details */}
              <div>
                <h4 className="font-medium mb-2">Technical Info</h4>
                <div className="space-y-1 text-sm text-muted-foreground">
                  {video.width && video.height && (
                    <div className="flex justify-between">
                      <span>Resolution:</span>
                      <span>{video.width}×{video.height}</span>
                    </div>
                  )}
                  {video.fps && (
                    <div className="flex justify-between">
                      <span>Frame Rate:</span>
                      <span>{video.fps.toFixed(1)} fps</span>
                    </div>
                  )}
                  {video.codec && (
                    <div className="flex justify-between">
                      <span>Codec:</span>
                      <span>{video.codec.toUpperCase()}</span>
                    </div>
                  )}
                  {video.file_size && (
                    <div className="flex justify-between">
                      <span>File Size:</span>
                      <span>{formatFileSize(video.file_size)}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Available Resolutions */}
              {video.resolutions && video.resolutions.length > 0 && (
                <div>
                  <h4 className="font-medium mb-2">Available Resolutions</h4>
                  <div className="space-y-1">
                    {video.resolutions.map((res) => (
                      <div key={res.id} className="flex justify-between text-sm">
                        <span>{res.resolution}</span>
                        <span className="text-muted-foreground">
                          {formatFileSize(res.file_size)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default VideoPage;
