import React from 'react';
import './SummaryCards.css';

function formatNumber(n) {
  if (n >= 1e9) return (n / 1e9).toFixed(2) + 'B';
  if (n >= 1e6) return (n / 1e6).toFixed(2) + 'M';
  if (n >= 1e3) return (n / 1e3).toFixed(2) + 'K';
  return Number(n).toLocaleString();
}

function formatCurrency(n) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
    minimumFractionDigits: 0,
  }).format(n);
}

function SummaryCards({ totalTransactions, totalAmount, uniqueCustomers }) {
  return (
    <div className="summary-cards">
      <div className="card">
        <span className="card-label">Total Transactions</span>
        <span className="card-value">{formatNumber(totalTransactions ?? 0)}</span>
      </div>
      <div className="card">
        <span className="card-label">Total Amount</span>
        <span className="card-value">{formatCurrency(totalAmount ?? 0)}</span>
      </div>
      <div className="card">
        <span className="card-label">Unique Customers</span>
        <span className="card-value">{formatNumber(uniqueCustomers ?? 0)}</span>
      </div>
    </div>
  );
}

export default SummaryCards;
