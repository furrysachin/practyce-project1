import React from 'react';
import SummaryCards from './SummaryCards';
import './FileSummarySection.css';

function FileSummarySection({ data }) {
  const dist = data.transaction_type_distribution || [];
  return (
    <div className="file-summary">
      <SummaryCards
        totalTransactions={data.total_transactions}
        totalAmount={data.total_amount}
        uniqueCustomers={data.unique_customers}
      />
      {data.file_name && (
        <p className="file-meta">
          File: <strong>{data.file_name}</strong>
          {data.source_batch && ` · Batch: ${data.source_batch}`}
        </p>
      )}
      {dist.length > 0 && (
        <div className="type-distribution">
          <h3>Transaction type distribution</h3>
          <ul>
            {dist.map((item, i) => (
              <li key={i}>
                <span className="type-name">{item.transaction_type}</span>
                <span className="type-count">{item.count}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default FileSummarySection;
