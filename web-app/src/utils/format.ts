/**
 * NCR Property Intelligence - Currency Formatting Utility
 * Standardizes price display across the platform (₹ Cr / ₹ L).
 */

export function formatNCRPrice(value: number | string | undefined | null): string {
  if (value === undefined || value === null || value === '') return '--';
  
  const rawNum = typeof value === 'string' ? parseFloat(value.replace(/[^0-9.]/g, '')) : value;
  if (isNaN(rawNum)) return '--';
  
  // High-Alpha Formatting: We round to integers for absolute currency
  const num = Math.round(rawNum);

  if (num >= 10000000) {
    const cr = num / 10000000;
    return `₹${cr % 1 === 0 ? cr : cr.toFixed(2)} Cr`;
  } else if (num >= 100000) {
    const l = num / 100000;
    return `₹${l % 1 === 0 ? l : l.toFixed(1)} L`;
  } else if (num >= 1000) {
    const k = num / 1000;
    return `₹${k % 1 === 0 ? k : k.toFixed(1)} K`;
  }
  
  return `₹${num.toLocaleString('en-IN')}`;
}

/**
 * Standardizes area display (Sq.Ft) - Always integer precision
 */
export function formatArea(value: number | string | undefined | null): string {
  if (value === undefined || value === null) return '--';
  const rawNum = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(rawNum)) return '--';
  return `${Math.round(rawNum).toLocaleString('en-IN')} Sq.Ft`;
}
