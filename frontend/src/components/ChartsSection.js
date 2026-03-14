import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import './ChartsSection.css';

const CHART_COLORS = ['#38bdf8', '#34d399', '#fbbf24', '#a78bfa', '#f472b6', '#2dd4bf', '#fb923c', '#818cf8'];

function ChartsSection({ overall, fileSummary, transactionsPerFile }) {
  const typeData = (fileSummary?.transaction_type_distribution || overall?.transaction_type_distribution) || [];
  const typeChartData = typeData.map((d) => ({
    name: d.transaction_type || 'Unknown',
    value: d.count,
    count: d.count,
  }));

  const topMerchants = (overall?.top_merchants || []).map((m) => ({
    name: m.merchant_name?.length > 18 ? m.merchant_name.slice(0, 18) + '…' : m.merchant_name,
    fullName: m.merchant_name,
    count: m.transaction_count,
    amount: m.total_amount,
  }));

  const fileChartData = (transactionsPerFile || []).map((f) => ({
    name: f.file_name?.replace(/\.json$/, '') || `Batch ${f.batch_id}`,
    count: f.transaction_count,
  }));

  const accountData = (overall?.most_active_accounts || []).map((a) => ({
    name: `Acc ${String(a.account_number).slice(-6)}`,
    count: a.transaction_count,
  }));

  const hasAny =
    typeChartData.length > 0 ||
    topMerchants.length > 0 ||
    fileChartData.length > 0 ||
    accountData.length > 0;

  if (!hasAny) {
    return (
      <section className="section charts-section">
        <h2>Analytics Charts</h2>
        <p className="muted">Upload files and load data to see charts.</p>
      </section>
    );
  }

  return (
    <section className="section charts-section">
      <h2>Analytics Charts</h2>
      <div className="charts-grid">
        {typeChartData.length > 0 && (
          <div className="chart-card">
            <h3>Transaction types</h3>
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={typeChartData} layout="vertical" margin={{ left: 10, right: 20, top: 10, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" horizontal={false} />
                <XAxis type="number" stroke="var(--text-muted)" tick={{ fontSize: 11 }} />
                <YAxis type="category" dataKey="name" width={110} stroke="var(--text-muted)" tick={{ fontSize: 11, fill: 'var(--text)' }} />
                <Tooltip
                  formatter={(value) => [value, 'Count']}
                  contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', color: 'var(--text)', borderRadius: '8px' }}
                />
                <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                  {typeChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {topMerchants.length > 0 && (
          <div className="chart-card">
            <h3>Top merchants (by tx count)</h3>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={topMerchants} layout="vertical" margin={{ left: 20, right: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis type="number" stroke="var(--text-muted)" />
                <YAxis type="category" dataKey="name" width={90} stroke="var(--text-muted)" tick={{ fontSize: 11 }} />
                <Tooltip
                  formatter={(value, name) => [name === 'amount' ? value?.toLocaleString() : value, name === 'amount' ? 'Amount' : 'Transactions']}
                  contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}
                  labelFormatter={(_, payload) => payload[0]?.payload?.fullName}
                />
                <Bar dataKey="count" fill="var(--accent)" name="Transactions" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {fileChartData.length > 0 && (
          <div className="chart-card">
            <h3>Transactions per file</h3>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={fileChartData} margin={{ top: 10, right: 10, left: 10, bottom: 60 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis dataKey="name" stroke="var(--text-muted)" angle={-35} textAnchor="end" height={60} tick={{ fontSize: 10 }} />
                <YAxis stroke="var(--text-muted)" />
                <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }} />
                <Bar dataKey="count" fill="var(--accent)" name="Transactions" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {accountData.length > 0 && (
          <div className="chart-card">
            <h3>Account activity (top accounts)</h3>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={accountData} margin={{ top: 10, right: 10, left: 10, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis dataKey="name" stroke="var(--text-muted)" />
                <YAxis stroke="var(--text-muted)" />
                <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }} />
                <Bar dataKey="count" fill="var(--accent)" name="Transactions" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </section>
  );
}

export default ChartsSection;
