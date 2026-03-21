import React, { useState, useEffect, useMemo } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { HomeView } from './components/HomeView';
import { ResultsView } from './components/ResultsView';
import { SearchResult } from './types';

const RESULTS_PER_PAGE = 10;

export default function App() {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  
  const [query, setQuery] = useState(searchParams.get('q') || '');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [hasSearched, setHasSearched] = useState(false);
  const [loading, setLoading] = useState(false);
  const [searchTime, setSearchTime] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [reindexing, setReindexing] = useState(false);

  // Sync state with URL params
  const urlQuery = searchParams.get('q');
  useEffect(() => {
    if (urlQuery) {
      setQuery(urlQuery);
      performSearch(urlQuery);
    } else {
      setHasSearched(false);
      setResults([]);
    }
  }, [urlQuery]);

  const handleReindex = async () => {
    if (reindexing) return;
    
    const confirmed = window.confirm("Bạn có chắc chắn muốn lập lại toàn bộ chỉ mục? Quá trình này sẽ mất một vài giây để quét lại toàn bộ dữ liệu.");
    if (!confirmed) return;

    setReindexing(true);
    
    toast.promise(
      fetch('http://localhost:3005/api/v1/reindex', { method: 'POST' })
        .then(res => res.json()),
      {
        loading: 'Đang lập lại chỉ mục dữ liệu...',
        success: (data) => data.message || "Đã cập nhật chỉ mục thành công!",
        error: 'Lỗi khi lập chỉ mục. Vui lòng kiểm tra server.',
        finally: () => setReindexing(false)
      }
    );
  };

  const performSearch = async (searchTerm: string) => {
    if (!searchTerm.trim()) return;

    setLoading(true);
    setHasSearched(true);
    setCurrentPage(1);
    const startTime = performance.now();

    try {
      let searchType = "keyword";
      let cleanQuery = searchTerm.trim();
      if (cleanQuery.startsWith('"') && cleanQuery.endsWith('"') && cleanQuery.length > 2) {
        searchType = "phrase";
        cleanQuery = cleanQuery.substring(1, cleanQuery.length - 1);
      }

      const response = await fetch(`http://localhost:3005/api/v1/search?q=${encodeURIComponent(cleanQuery)}&type=${searchType}`);
      const data = await response.json();
      
      const mappedResults: SearchResult[] = (data.results || []).map((item: any) => ({
        title: item.doc_id,
        url: `http://localhost:3005/dataset/${item.doc_id}`,
        snippet: `Điểm số: ${item.score.toFixed(4)}. Tìm thấy bằng phương pháp ${searchType === 'phrase' ? 'Tìm kiếm mệnh đề' : 'Tìm kiếm từ khóa'}.`
      }));

      setResults(mappedResults);
      setSearchTime((performance.now() - startTime) / 1000);
    } catch (error) {
      console.error("Search failed:", error);
      toast.error("Không thể kết nối tới máy chủ tìm kiếm.");
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;
    
    // Update URL which triggers useEffect
    setSearchParams({ q: query });
  };

  const resetSearch = () => {
    setQuery('');
    setSearchParams({});
    setHasSearched(false);
  };

  const paginatedResults = useMemo(() => {
    const startIndex = (currentPage - 1) * RESULTS_PER_PAGE;
    return results.slice(startIndex, startIndex + RESULTS_PER_PAGE);
  }, [results, currentPage]);

  const totalPages = Math.ceil(results.length / RESULTS_PER_PAGE);

  if (!hasSearched && !urlQuery) {
    return (
      <HomeView 
        query={query} 
        setQuery={setQuery} 
        handleSearch={handleSearch} 
        onReindex={handleReindex}
        reindexing={reindexing}
      />
    );
  }

  return (
    <ResultsView
      query={query}
      setQuery={setQuery}
      handleSearch={handleSearch}
      resetSearch={resetSearch}
      loading={loading}
      searchTime={searchTime}
      totalResults={results.length}
      results={paginatedResults}
      currentPage={currentPage}
      totalPages={totalPages}
      onPageChange={setCurrentPage}
      hasSearched={hasSearched}
      onReindex={handleReindex}
      reindexing={reindexing}
    />
  );
}
