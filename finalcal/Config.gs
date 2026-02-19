/**
 * ============================================================
 * CONFIG.GS - Cấu hình hệ thống Chatbot Quản Lý Tài Chính
 * ============================================================
 * 
 * HƯỚNG DẪN: Thay thế các giá trị "DÁN_..._VÀO_ĐÂY" bằng
 * API key thực tế của bạn trước khi chạy.
 */

// ==================== API KEYS ====================
const GEMINI_API_KEY = "DÁN_GEMINI_API_KEY_VÀO_ĐÂY";
const TELEGRAM_TOKEN = "DÁN_TELEGRAM_BOT_TOKEN_VÀO_ĐÂY";

// Chat ID của chủ sở hữu bot (để gửi nhắc nhở tự động)
// Gửi /start cho bot, sau đó chạy hàm getUpdates() để lấy chat_id
const OWNER_CHAT_ID = "DÁN_CHAT_ID_VÀO_ĐÂY";

// ==================== GOOGLE SHEETS ====================
// Tên các Tab trong Google Sheets
const SHEET_TRANSACTION = "Transaction";
const SHEET_DASHBOARD = "Dashboard";
const SHEET_DEBT = "Debt";

// ==================== THÔNG TIN NỢ ====================
const DEBTS = [
  {
    name: "TCB",
    fullName: "Techcombank",
    balance: 8900000,
    monthlyRate: 0.03,     // 3%/tháng
    annualRate: 0.36,       // 36%/năm
    payDay: 5,              // Mùng 5 hàng tháng
    monthlyPayment: 1000000, // Trả tối thiểu 1tr
    type: "credit_card"
  },
  {
    name: "MOMO",
    fullName: "Momo",
    balance: 27200000,
    monthlyRate: 0.036,    // 3.6%/tháng
    annualRate: 0.432,      // 43.2%/năm
    payDay: 13,             // Ngày 13 hàng tháng
    monthlyPayment: 3400000, // Trả góp 3.4tr
    type: "installment"
  },
  {
    name: "VP",
    fullName: "VP Bank",
    balance: 80000000,
    monthlyRate: 0.032,    // 3.2%/tháng
    annualRate: 0.384,      // 38.4%/năm
    payDay: 15,             // Ngày 15 hàng tháng
    monthlyPayment: 4700000, // Trả góp 4.7tr
    type: "installment"
  },
  {
    name: "TP",
    fullName: "TP Bank",
    balance: 14997000,
    monthlyRate: 0.015,    // 1.5%/tháng
    annualRate: 0.18,       // 18%/năm
    payDay: 25,             // Ngày 25 hàng tháng
    monthlyPayment: 1000000, // Trả tối thiểu 1tr
    type: "credit_card"
  },
  {
    name: "HANH",
    fullName: "Hạnh",
    balance: 15000000,
    monthlyRate: 0,
    annualRate: 0,
    payDay: null,
    monthlyPayment: 0,
    type: "personal"
  },
  {
    name: "TIN",
    fullName: "Tú/Tín",
    balance: 8000000,
    monthlyRate: 0,
    annualRate: 0,
    payDay: null,
    monthlyPayment: 0,
    type: "personal"
  }
];

// ==================== TIỀN NHÀ ====================
const RENT = {
  amount: 18000000,           // 18 triệu
  cycleMonths: 3,             // Mỗi 3 tháng
  nextPayDates: ["2026-04-20", "2026-07-20", "2026-10-20", "2027-01-20"],
  dailySaving: 200000          // Cần tích lũy 200k/ngày cho tiền nhà
};

// ==================== KINH DOANH ====================
const BUSINESS = {
  profitMargin: 0.60,           // Biên lợi nhuận 60%
  monthlyShareOffice: 2000000,  // Thu nhập share văn phòng: 2tr/tháng
  targetDailyRevenue: 978000,   // Doanh thu mục tiêu/ngày
  targetDailyAccumulation: 587000 // Tích lũy mục tiêu/ngày
};

// ==================== TỔNG NỢ HÀNG THÁNG ====================
// Tổng tiền phải trả hàng tháng (gốc + lãi các khoản ngân hàng)
const TOTAL_MONTHLY_DEBT_PAYMENT = DEBTS
  .filter(d => d.monthlyPayment > 0)
  .reduce((sum, d) => sum + d.monthlyPayment, 0); // = 10,100,000

// ==================== DANH MỤC CHI TIÊU ====================
const CATEGORIES = {
  income: ["Bán hàng", "Share văn phòng", "Adsense", "Oreka", "Khác"],
  expense: ["Ăn uống", "Cafe", "Xăng xe", "Điện nước", "Phụ phí", 
            "Trả nợ", "Tiền nhà", "Ads", "Lương NV", "Nhập hàng", "Khác"]
};

// ==================== NGƯỠNG CẢNH BÁO ====================
const ALERTS = {
  debtReminderDaysBefore: 7,    // Nhắc trước 7 ngày
  dailyReminderHour: 8,         // Nhắc lúc 8h sáng
  cafeBudgetWeekly: 200000,     // Ngân sách cafe tối đa/tuần
  miscBudgetMonthly: 500000     // Ngân sách phụ phí tối đa/tháng
};
