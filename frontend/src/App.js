import React, { useState, useEffect, useCallback } from 'react';
import { uploadJsonFile, getFileSummary, getOverallSummary, getBatches, getTransactionsPerFile } from './api/client';
import SummaryCards from './components/SummaryCards';
import FileSummarySection from './components/FileSummarySection';
import ChartsSection from './components/ChartsSection';
import UploadSection from './components/UploadSection';
import './App.css';

function App() {
  const [overall, setOverall] = useState(null);
  const [fileSummary, setFileSummary] = useState(null);
  const [batches, setBatches] = useState([]);
  const [transactionsPerFile, setTransactionsPerFile] = useState([]);
  const [selectedBatchId, setSelectedBatchId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  const fetchOverall = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getOverallSummary();
      setOverall(data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to load overall summary');
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchBatches = useCallback(async () => {
    try {
      const data = await getBatches();
      setBatches(data);
      if (data.length && !selectedBatchId) setSelectedBatchId(data[0].batch_id);
    } catch (err) {
      console.warn('Batches load failed', err);
    }
  }, [selectedBatchId]);

  const fetchTransactionsPerFile = useCallback(async () => {
    try {
      const data = await getTransactionsPerFile();
      setTransactionsPerFile(data);
    } catch (err) {
      console.warn('Transactions per file failed', err);
    }
  }, []);

  const fetchFileSummary = useCallback(async (batchId) => {
    if (!batchId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getFileSummary(batchId);
      setFileSummary(data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to load file summary');
      setFileSummary(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchOverall();
    fetchBatches();
    fetchTransactionsPerFile();
  }, [fetchOverall, fetchBatches, fetchTransactionsPerFile]);

  useEffect(() => {
    if (selectedBatchId) fetchFileSummary(selectedBatchId);
    else setFileSummary(null);
  }, [selectedBatchId, fetchFileSummary]);

  const handleUpload = async (file) => {
    setUploading(true);
    setError(null);
    try {
      await uploadJsonFile(file);
      await fetchOverall();
      await fetchBatches();
      await fetchTransactionsPerFile();
      const list = await getBatches();
      if (list.length) setSelectedBatchId(list[0].batch_id);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Retail Banking Transaction Analytics</h1>
        <p className="subtitle">Ingest, normalize, and analyze transaction data</p>
      </header>

      {error && (
        <div className="error-banner" role="alert">
          {error}
        </div>
      )}

      <UploadSection onUpload={handleUpload} uploading={uploading} />

      <section className="section">
        <h2>Overall Analytics</h2>
        {loading && !overall ? (
          <p className="loading">Loading…</p>
        ) : overall ? (
          <SummaryCards
            totalTransactions={overall.total_transactions_all_files}
            totalAmount={overall.total_transaction_volume}
            uniqueCustomers={overall.unique_customers_overall}
          />
        ) : (
          <p className="muted">Upload a JSON file to see overall metrics.</p>
        )}
      </section>

      <section className="section">
        <h2>File Summary</h2>
        {batches.length > 0 && (
          <div className="batch-select">
            <label htmlFor="batch-select">Select file (batch): </label>
            <select
              id="batch-select"
              value={selectedBatchId ?? ''}
              onChange={(e) => setSelectedBatchId(e.target.value ? Number(e.target.value) : null)}
            >
              <option value="">-- Select --</option>
              {batches.map((b) => (
                <option key={b.batch_id} value={b.batch_id}>
                  {b.file_name} (batch {b.batch_id})
                </option>
              ))}
            </select>
          </div>
        )}
        {loading && selectedBatchId && !fileSummary ? (
          <p className="loading">Loading file summary…</p>
        ) : fileSummary ? (
          <FileSummarySection data={fileSummary} />
        ) : batches.length === 0 ? (
          <p className="muted">No files uploaded yet.</p>
        ) : (
          <p className="muted">Select a file above.</p>
        )}
      </section>

      <ChartsSection
        overall={overall}
        fileSummary={fileSummary}
        transactionsPerFile={transactionsPerFile}
      />
    </div>
  );
}

export default App;
