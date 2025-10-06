import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useSearchParams } from 'react-router-dom';
import { videosAPI, categoriesAPI } from '../lib/api';
import VideoGrid from '../components/video/VideoGrid';
import VideoFilters from '../components/video/VideoFilters';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { RefreshCw } from 'lucide-react';

const HomePage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [filters, setFilters] = useState({
    search: searchParams.get('search') || '',
    category_id: searchParams.get('category_id') || '',
    uploader_id: searchParams.get('uploader_id') || '',
    page: parseInt(searchParams.get('page')) || 1,
    per_page: 20,
  });

  // Update filters when URL params change
  useEffect(() => {
    setFilters(prev => ({
      ...prev,
      search: searchParams.get('search') || '',
      category_id: searchParams.get('category_id') || '',
      uploader_id: searchParams.get('uploader_id') || '',
      page: parseInt(searchParams.get('page')) || 1,
    }));
  }, [searchParams]);

  // Fetch videos
  const {
    data: videosData,
    isLoading: videosLoading,
    error: videosError,
    refetch: refetchVideos,
  } = useQuery({
    queryKey: ['videos', filters],
    queryFn: () => videosAPI.getVideos(filters),
    keepPreviousData: true,
  });

  // Fetch categories for filters
  const {
    data: categoriesData,
    isLoading: categoriesLoading,
  } = useQuery({
    queryKey: ['categories'],
    queryFn: () => categoriesAPI.getCategories(),
  });

  const handleFilterChange = (newFilters) => {
    const updatedFilters = { ...filters, ...newFilters, page: 1 };
    setFilters(updatedFilters);

    // Update URL params
    const params = new URLSearchParams();
    Object.entries(updatedFilters).forEach(([key, value]) => {
      if (value && key !== 'per_page') {
        params.set(key, value.toString());
      }
    });
    setSearchParams(params);
  };

  const handlePageChange = (page) => {
    const updatedFilters = { ...filters, page };
    setFilters(updatedFilters);

    const params = new URLSearchParams(searchParams);
    params.set('page', page.toString());
    setSearchParams(params);
  };

  if (videosError) {
    return (
      <div className="space-y-4">
        <Alert variant="destructive">
          <AlertDescription>
            Failed to load videos. Please try again.
          </AlertDescription>
        </Alert>
        <Button onClick={() => refetchVideos()} variant="outline">
          <RefreshCw className="mr-2 h-4 w-4" />
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">
          {filters.search ? `Search Results for "${filters.search}"` : 'Discover Videos'}
        </h1>
        <p className="text-muted-foreground">
          Browse and watch videos from our community
        </p>
      </div>

      {/* Filters */}
      <VideoFilters
        filters={filters}
        categories={categoriesData?.data?.categories || []}
        onFilterChange={handleFilterChange}
        loading={categoriesLoading}
      />

      {/* Videos Grid */}
      {videosLoading ? (
        <div className="flex justify-center py-12">
          <LoadingSpinner size="lg" />
        </div>
      ) : (
        <VideoGrid
          videos={videosData?.data?.videos || []}
          pagination={videosData?.data?.pagination}
          onPageChange={handlePageChange}
          loading={videosLoading}
        />
      )}

      {/* Empty State */}
      {!videosLoading && (!videosData?.data?.videos || videosData.data.videos.length === 0) && (
        <div className="text-center py-12">
          <div className="mx-auto max-w-md">
            <h3 className="text-lg font-medium text-foreground mb-2">
              No videos found
            </h3>
            <p className="text-muted-foreground mb-4">
              {filters.search || filters.category_id
                ? 'Try adjusting your search criteria or filters.'
                : 'Be the first to upload a video to get started!'}
            </p>
            {!filters.search && !filters.category_id && (
              <Button onClick={() => window.location.href = '/upload'}>
                Upload Video
              </Button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default HomePage;
