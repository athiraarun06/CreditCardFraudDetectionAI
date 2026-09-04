export const CURRENCIES = ["INR", "USD", "EUR", "GBP"];
export const MERCHANT_CATEGORIES = ["grocery", "electronics", "travel", "dining", "fuel", "online", "entertainment", "other"];
export const CITIES = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune", "Ahmedabad", "Jaipur", "Lucknow"];
export const COUNTRIES = ["India", "USA", "UK", "Germany", "Russia", "China", "UAE", "Singapore"];
export const PAYMENT_METHODS = ["Credit Card", "Debit Card", "UPI", "Wallet", "Net Banking"];
export const CARD_TYPES = ["Visa", "Mastercard", "RuPay", "Amex"];
export const DEVICE_TYPES = ["Android", "iPhone", "Web", "POS Terminal"];
export const OS_LIST = ["Android 14", "iOS 17", "Windows 11", "macOS", "Linux"];
export const BROWSERS = ["Chrome", "Safari", "Firefox", "Edge", "App"];
export const GENDERS = ["Male", "Female", "Other"];
export const RISK_PROFILES = ["Low", "Medium", "High"];

export function randomIp() {
  return `${Math.floor(Math.random() * 223) + 1}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`;
}

export function randomDeviceId() {
  return `DEV-${Math.random().toString(36).slice(2, 10).toUpperCase()}`;
}

export function nowLocalDatetime() {
  const d = new Date();
  d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
  return d.toISOString().slice(0, 16);
}
