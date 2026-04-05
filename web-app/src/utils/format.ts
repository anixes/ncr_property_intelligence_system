/**
 * NCR Property Intelligence - Currency Formatting Utility
 * Standardizes price display across the platform (₹ Cr / ₹ L).
 */

export function formatNCRPrice(value: number | string | undefined | null): string {
  if (value === undefined || value === null || value === '') return '--';
  
  const num = typeof value === 'string' ? parseFloat(value.replace(/[^0-9.]/g, '')) : value;
  
  if (isNaN(num)) return '--';

  // 1 Crore = 1,00,00,000 (10^7)
  // 1 Lakh = 1,00,000 (10^5)
  
  if (num >= 10000000) {
    return `₹${(num / 10000000).toFixed(2)} Cr`;
  } else if (num >= 100000) {
    return `₹${(num / 100000).toFixed(1)} L`;
  } else if (num >= 1000) {
    return `₹${(num / 1000).toFixed(1)} K`;
  }
  
  return `₹${num.toLocaleString('en-IN')}`;
}

/**
 * Standardizes area display (Sq.Ft)
 */
export function formatArea(value: number | string | undefined | null): string {
  if (!value) return '--';
  const num = typeof value === 'string' ? parseFloat(value) : value;
  return `${num.toLocaleString('en-IN')} Sq.Ft`;
}
