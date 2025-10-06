import React from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Card, CardContent } from '@/components/ui/card';
import { X, Filter } from 'lucide-react';

const VideoFilters = ({ filters, categories, onFilterChange, loading }) => {
  const handleSearchChange = (e) => {
    onFilterChange({ search: e.target.value });
  };

  const handleCategoryChange = (value) => {
    onFilterChange({ category_id: value === 'all' ? '' : value });
  };

  const clearFilters = () => {
    onFilterChange({
      search: '',
      category_id: '',
      uploader_id: '',
    });
  };

  const hasActiveFilters = filters.search || filters.category_id || filters.uploader_id;

  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center space-x-2 mb-4">
          <Filter className="h-4 w-4" />
          <Label className="text-sm font-medium">Filters</Label>
          {hasActiveFilters && (
            <Button
              variant="ghost"
              size="sm"
              onClick={clearFilters}
              className="ml-auto"
            >
              <X className="h-4 w-4 mr-1" />
              Clear
            </Button>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Search */}
          <div className="space-y-2">
            <Label htmlFor="search" className="text-sm">Search</Label>
            <Input
              id="search"
              type="text"
              placeholder="Search videos..."
              value={filters.search}
              onChange={handleSearchChange}
            />
          </div>

          {/* Category Filter */}
          <div className="space-y-2">
            <Label className="text-sm">Category</Label>
            <Select
              value={filters.category_id || 'all'}
              onValueChange={handleCategoryChange}
              disabled={loading}
            >
              <SelectTrigger>
                <SelectValue placeholder="All categories" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All categories</SelectItem>
                {categories.map((category) => (
                  <SelectItem key={category.id} value={category.id.toString()}>
                    {category.name}
                    {category.is_shared && ' (Shared)'}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Sort Options (Future Enhancement) */}
          <div className="space-y-2">
            <Label className="text-sm">Sort by</Label>
            <Select defaultValue="newest">
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="newest">Newest first</SelectItem>
                <SelectItem value="oldest">Oldest first</SelectItem>
                <SelectItem value="title">Title A-Z</SelectItem>
                <SelectItem value="duration">Duration</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Active Filters Display */}
        {hasActiveFilters && (
          <div className="mt-4 pt-4 border-t">
            <div className="flex flex-wrap gap-2">
              {filters.search && (
                <div className="flex items-center bg-primary/10 text-primary px-2 py-1 rounded-md text-sm">
                  <span>Search: "{filters.search}"</span>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="ml-1 h-auto p-0"
                    onClick={() => onFilterChange({ search: '' })}
                  >
                    <X className="h-3 w-3" />
                  </Button>
                </div>
              )}
              
              {filters.category_id && (
                <div className="flex items-center bg-primary/10 text-primary px-2 py-1 rounded-md text-sm">
                  <span>
                    Category: {categories.find(c => c.id.toString() === filters.category_id)?.name}
                  </span>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="ml-1 h-auto p-0"
                    onClick={() => onFilterChange({ category_id: '' })}
                  >
                    <X className="h-3 w-3" />
                  </Button>
                </div>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default VideoFilters;
