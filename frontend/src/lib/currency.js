// India-first currency formatting: ₹ symbol with Indian digit grouping (lakhs/crores),
// e.g. ₹1,50,000.00 rather than the US-style ₹150,000.00.
const inrFormatter = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

const inrFormatterNoDecimals = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  minimumFractionDigits: 0,
  maximumFractionDigits: 0,
});

export function formatINR(amount, { decimals = true } = {}) {
  const value = Number(amount) || 0;
  return decimals ? inrFormatter.format(value) : inrFormatterNoDecimals.format(value);
}
