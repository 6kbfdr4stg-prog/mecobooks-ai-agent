/**
 * ============================================================
 * CONFIG.GS - Cấu hình hệ thống Chatbot Quản Lý Tài Chính
 * ============================================================
 * 
 * HƯỚNG DẪN: Thay thế các giá trị "DÁN_..._VÀO_ĐÂY" bằng
 * API key thực tế của bạn trước khi chạy.
 */

// ==================== API KEYS ====================
// ==================== API KEYS ====================
const GEMINI_API_KEY = "AIzaSyCtq3Bqky_uOu7d4qNsPJVbUE1yO5csHRI"; 
const TELEGRAM_TOKEN = "8292481641:AAHfTK91TWpvjVAb7j-YtK1LP-AVDkuOcuo";
const GEMINI_MODEL_FAST = "gemini-2.0-flash";
const GEMINI_MODEL_SMART = "gemini-1.5-pro"; // Revert to stable 1.5 Pro

// Chat ID của chủ sở hữu bot (để gửi nhắc nhở tự động)
// Gửi /start cho bot, sau đó chạy hàm getUpdates() để lấy chat_id
const OWNER_CHAT_ID = "8425705625"; // Đã cập nhật ID chính chủ

// Danh sách user được phép dùng bot (thêm chatId vào đây)
var ALLOWED_USERS = [OWNER_CHAT_ID];
// VD thêm user: ALLOWED_USERS = [OWNER_CHAT_ID, "123456789", "987654321"];

// ==================== HARAVAN API ====================
// Lấy token từ: Admin Haravan → Apps → Private apps → Tạo app → Copy token
// Cần quyền: com.read_orders, com.read_products
const HARAVAN_TOKEN = "04A58A8AECB66442E639FB7BC5C9B189E6B563EBE56442BA0FE907BD29FB1845";
const HARAVAN_SHOP = "tiem-sach-anh-tuan"; // tiem-sach-anh-tuan.myharavan.com
const HARAVAN_API_BASE = "https://apis.haravan.com/com";
// Danh mục doanh thu từ Haravan sẽ ghi vào sheet
const HARAVAN_REVENUE_CATEGORY = "Bán hàng"; // Đổi thành danh mục có sẵn trong Sheet
// Chế độ sync: "paid" (chỉ đơn đã TT) hoặc "all" (tính cả đơn chờ/COD)
const HARAVAN_SYNC_MODE = "all";
// Token bảo mật Casso (lấy từ https://casso.vn/secure-token)
const CASSO_SECURE_TOKEN = "DÁN_CASSO_TOKEN_VÀO_ĐÂY";

// ==================== GOOGLE SHEETS ====================
// ID của Google Sheets hiện có (chứa dữ liệu chi tiêu)
const SPREADSHEET_ID = "1zBKIHlE-skicPBAkf7OHARIIG27c72PlJu8upd9vRqc";
// Tab tháng format: "MM-YYYY" (VD: "02-2026", "01-2026")

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
  amount: 6000000,            // 6 triệu/tháng (thuê nhà hàng tháng)
  cycleMonths: 1,             // Mỗi tháng
  nextPayDates: ["2026-03-01", "2026-04-01", "2026-05-01", "2026-06-01"],
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
  cafeBudgetWeekly: 500000,     // Ngân sách cafe tối đa/tuần (~2tr/tháng thực tế)
  miscBudgetMonthly: 3000000    // Ngân sách phụ phí tối đa/tháng (~3tr thực tế)
};
/**
 * ============================================================
 * GEMINI SERVICE - Gọi Gemini API để phân tích giao dịch
 * ============================================================
 */

/**
 * Gọi Gemini API với prompt
 * @param {string} prompt - Nội dung gửi cho Gemini
 * @param {string} systemInstruction - System prompt (tùy chọn)
 * @param {string} modelName - Tên model (tùy chọn, mặc định gemini-2.0-flash)
 * @returns {string} - Phản hồi từ Gemini
 */
function callGemini(prompt, systemInstruction, modelName) {
  // Kiểm tra prompt rỗng để tránh lỗi 400
  if (!prompt || typeof prompt !== 'string' || prompt.trim() === "") {
    Logger.log("⚠️ Prompt bị rỗng hoặc không hợp lệ. Bỏ qua gọi API.");
    return null;
  }

  var model = modelName || GEMINI_MODEL_FAST;
  const url = "https://generativelanguage.googleapis.com/v1beta/models/" + model + ":generateContent?key=" + GEMINI_API_KEY;
  
  var contents = [{"parts": [{"text": prompt}]}];
  
  var payload = {
    "contents": contents
  };
  
  if (systemInstruction) {
    payload["systemInstruction"] = {
      "parts": [{"text": systemInstruction}]
    };
  }
  
  // Cấu hình để trả về JSON
  payload["generationConfig"] = {
    "temperature": 0.1,
    "maxOutputTokens": 2048
  };
  
  var options = {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };
  
  try {
    var response = UrlFetchApp.fetch(url, options);
    var json = JSON.parse(response.getContentText());
    
    if (json.candidates && json.candidates[0] && json.candidates[0].content) {
      return json.candidates[0].content.parts[0].text;
    }
    
    Logger.log("Gemini error response: " + response.getContentText());
    return null;
  } catch (error) {
    Logger.log("Gemini API error: " + error.toString());
    return null;
  }
}

/**
 * Phân tích tin nhắn người dùng thành giao dịch
 * @param {string} userText - Tin nhắn từ người dùng
 * @returns {Object} - {amount, content, type, category}
 */
function parseTransaction(userText) {
  var systemPrompt = 'Bạn là trợ lý tài chính. Nhiệm vụ của bạn là phân tích tin nhắn của người dùng và trích xuất thông tin giao dịch.\n\n' +
    'Quy tắc:\n' +
    '- Nếu tin nhắn đề cập đến việc bán hàng, nhận tiền, doanh thu → type = "Thu"\n' +
    '- Nếu tin nhắn đề cập đến chi tiêu, mua sắm, ăn uống → type = "Chi"\n' +
    '- "k" hoặc "K" = nghìn (1000). Ví dụ: 50k = 50000, 1tr2 = 1200000\n' +
    '- "tr" hoặc "triệu" = triệu (1000000). Ví dụ: 1tr = 1000000\n' +
    '- Danh mục Thu: Bán hàng, Share văn phòng, Adsense, Oreka, Khác\n' +
    '- Danh mục Chi: Ăn uống, Cafe, Xăng xe, Điện nước, Phụ phí, Trả nợ, Tiền nhà, Ads, Lương NV, Nhập hàng, Khác\n\n' +
    'Trả về CHÍNH XÁC JSON (không markdown, không giải thích):\n' +
    '{"amount": <số_tiền_dạng_số>, "content": "<mô_tả_ngắn>", "type": "<Thu_hoặc_Chi>", "category": "<danh_mục>"}\n\n' +
    'Nếu tin nhắn KHÔNG phải giao dịch (ví dụ: hỏi thăm, yêu cầu báo cáo), trả về:\n' +
    '{"amount": 0, "content": "", "type": "none", "category": "none"}';

  var response = callGemini(userText, systemPrompt);
  
  if (!response) {
    return { amount: 0, content: "", type: "none", category: "none" };
  }
  
  try {
    // Loại bỏ markdown code block nếu có
    var cleaned = response.replace(/```json\s*/g, "").replace(/```\s*/g, "").trim();
    return JSON.parse(cleaned);
  } catch (e) {
    Logger.log("Parse error: " + e.toString() + " | Response: " + response);
    return { amount: 0, content: "", type: "none", category: "none" };
  }
}

/**
 * Lấy lời khuyên tài chính từ AI dựa trên context
 * @param {Object} context - Thông tin tài chính hiện tại
 * @returns {string} - Lời khuyên
 */
function getFinancialAdvice(context) {
  var systemPrompt = 'Bạn là cố vấn tài chính cá nhân nghiêm khắc nhưng động viên. ' +
    'Trả lời bằng tiếng Việt, ngắn gọn (tối đa 200 từ). ' +
    'Dùng emoji phù hợp. Tập trung vào hành động cụ thể. ' +
    'Luôn nhắc nhở ưu tiên trả nợ Momo (lãi 3.6%) và VP Bank (lãi 3.2%).';

  var prompt = "Đây là tình hình tài chính hiện tại:\n" + JSON.stringify(context, null, 2) + 
    "\n\nHãy đưa ra nhận xét ngắn gọn và 1-2 lời khuyên hành động cụ thể.";
  
    "\n\nHãy đưa ra nhận xét ngắn gọn và 1-2 lời khuyên hành động cụ thể.";
  
  // Use Pro model for smarter advice
  var response = callGemini(prompt, systemPrompt, GEMINI_MODEL_SMART);
  return response || "Không thể lấy lời khuyên lúc này. Hãy thử lại sau.";
}

/**
 * Xử lý câu hỏi tự do từ người dùng
 * @param {string} question - Câu hỏi
 * @param {Object} financialContext - Bối cảnh tài chính
 * @returns {string} - Câu trả lời
 */
function answerQuestion(question, financialContext) {
  var systemPrompt = 'Bạn là trợ lý tài chính cá nhân. Trả lời bằng tiếng Việt, ngắn gọn.\n' +
    'Thông tin tài chính của chủ sở hữu:\n' +
    '- Tổng nợ: 154,097,000đ (TCB 8.9tr, Momo 27.2tr, VP 80tr, TP 15tr, nợ cá nhân 23tr)\n' +
    '- Tiền lãi: ~4tr/tháng\n' +
    '- Tiền trả góp hàng tháng: 10.1tr (TCB 1tr ngày 5, Momo 3.4tr ngày 13, VP 4.7tr ngày 15, TP 1tr ngày 25)\n' +
    '- Tiền nhà: 18tr/3 tháng (mốc tiếp: 20/04)\n' +
    '- Doanh thu trung bình: 21tr/tháng, biên lợi nhuận 60%\n' +
    '- Thu nhập thêm: 2tr/tháng (share VP)\n' +
    '- Mục tiêu tích lũy: 587k/ngày\n\n' +
    'Dữ liệu thực tế hôm nay:\n' + JSON.stringify(financialContext, null, 2);

    'Dữ liệu thực tế hôm nay:\n' + JSON.stringify(financialContext, null, 2);

  // Use Pro model for Q&A
  var response = callGemini(question, systemPrompt, GEMINI_MODEL_SMART);
  return response || "Xin lỗi, tôi không thể trả lời câu hỏi này lúc này.";
}
/**
 * ============================================================
 * SHEET SERVICE - Đọc/Ghi dữ liệu Google Sheets
 * Kết nối trực tiếp với bảng tính chi tiêu hiện có
 * Format: Tab theo tháng (MM-YYYY), danh mục ở cột A, tổng tháng cột B
 * ============================================================
 */

// Mapping danh mục trong Sheet → danh mục bot
var CATEGORY_MAP = {
  "ĂN UỐNG": {type: "Chi", botCategory: "Ăn uống"},
  "CAFE": {type: "Chi", botCategory: "Cafe"},
  "PHỤ PHÍ": {type: "Chi", botCategory: "Phụ phí"},
  "THUÊ NHÀ": {type: "Chi", botCategory: "Tiền nhà"},
  "TRẢ LÃI": {type: "Chi", botCategory: "Trả nợ"},
  // Business Categories (isBusiness: true)
  "ADS": {type: "Chi", botCategory: "Ads", isBusiness: true},
  "QUẢNG CÁO": {type: "Chi", botCategory: "Ads", isBusiness: true},
  "VY": {type: "Chi", botCategory: "Lương NV", isBusiness: true},
  "LY": {type: "Chi", botCategory: "Lương NV", isBusiness: true},
  "LINH": {type: "Chi", botCategory: "Lương NV", isBusiness: true},
  "QUỲNH": {type: "Chi", botCategory: "Lương NV", isBusiness: true},
  "NHẬP HÀNG": {type: "Chi", botCategory: "Nhập hàng", isBusiness: true},
  "VẬN CHUYỂN": {type: "Chi", botCategory: "Vận chuyển", isBusiness: true},
  "BAO BÌ": {type: "Chi", botCategory: "Bao bì", isBusiness: true},
  "BÁN HÀNG": {type: "Thu", botCategory: "Bán hàng"},
  "PHÍ SHIP": {type: "Thu", botCategory: "Bán hàng"}
};

// Mapping ngược: từ bot category → sheet category
var BOT_TO_SHEET = {
  "Ăn uống": "ĂN UỐNG",
  "Cafe": "CAFE",
  "Phụ phí": "PHỤ PHÍ",
  "Ads": "ADS",
  "Tiền nhà": "THUÊ NHÀ",
  "Trả nợ": "TRẢ LÃI",
  "Lương NV": "VY",
  "Bán hàng": "BÁN HÀNG"
};

/**
 * Lấy Spreadsheet theo ID cố định
 */
function getSpreadsheet() {
  return SpreadsheetApp.openById(SPREADSHEET_ID);
}

/**
 * Lấy tên tab tháng hiện tại (format: MM-YYYY)
 */
function getCurrentMonthTab() {
  var now = new Date();
  var month = Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "MM");
  var year = Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "yyyy");
  return month + "-" + year;
}

/**
 * Lấy sheet của tháng hiện tại
 */
function getMonthSheet() {
  var ss = getSpreadsheet();
  var tabName = getCurrentMonthTab();
  var sheet = ss.getSheetByName(tabName);
  if (!sheet) {
    Logger.log("Không tìm thấy tab: " + tabName);
  }
  return sheet;
}

/**
 * Khởi tạo - Không cần tạo sheet mới, sử dụng sheet có sẵn
 */
function initializeSheets() {
  var ss = getSpreadsheet();
  var tabName = getCurrentMonthTab();
  var sheet = ss.getSheetByName(tabName);
  
  if (sheet) {
    Logger.log("✅ Đã kết nối tới sheet: " + ss.getName() + " / Tab: " + tabName);
    sendMessage(OWNER_CHAT_ID, "✅ Đã kết nối tới bảng tính: " + ss.getName() + "\nTab hiện tại: " + tabName);
  } else {
    Logger.log("❌ Không tìm thấy tab " + tabName + " trong sheet");
    sendMessage(OWNER_CHAT_ID, "❌ Không tìm thấy tab " + tabName + ". Các tab có: " + 
      ss.getSheets().map(function(s){return s.getName();}).join(", "));
  }
}

/**
 * Tìm cột của ngày hôm nay trong sheet tháng
 * Dòng 1 chứa header ngày: [empty] | [tổng tháng] | 01/MM/YYYY | 02/MM/YYYY | ...
 * @returns {number} - Chỉ số cột (1-indexed), hoặc -1 nếu không tìm thấy
 */
function findTodayColumn(sheet) {
  if (!sheet) return -1;
  
  var now = new Date();
  var todayStr = Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "d"); // "1".."31"
  var today = parseInt(todayStr);
  
  // Cột C (index 3) = ngày 1, cột D (index 4) = ngày 2, ...
  // Vậy cột của ngày today = today + 2
  return today + 2;
}

/**
 * Tìm hàng của danh mục trong sheet
 * @param {Object} sheet - Sheet object
 * @param {string} categoryName - Tên danh mục (VD: "ĂN UỐNG")
 * @returns {number} - Chỉ số hàng (1-indexed), hoặc -1
 */
function findCategoryRow(sheet, categoryName) {
  if (!sheet) return -1;
  
  var lastRow = sheet.getLastRow();
  if (lastRow < 1) return -1;
  
  var categories = sheet.getRange(1, 1, lastRow, 1).getValues();
  for (var i = 0; i < categories.length; i++) {
    if (String(categories[i][0]).toUpperCase().trim() === categoryName.toUpperCase().trim()) {
      return i + 1; // 1-indexed
    }
  }
  return -1;
}

/**
 * Ghi một giao dịch vào tab tháng hiện tại
 * Cộng thêm số tiền vào đúng ô [danh mục, ngày hôm nay]
 */
function logTransaction(content, amount, type, category) {
  try {
    var sheet = getMonthSheet();
    if (!sheet) {
      Logger.log("Không tìm thấy tab tháng để ghi giao dịch");
      return;
    }
    
    // Tìm danh mục tương ứng trong sheet
    var sheetCategory = BOT_TO_SHEET[category] || category.toUpperCase();
    var row = findCategoryRow(sheet, sheetCategory);
    var col = findTodayColumn(sheet);
    
    if (row === -1) {
      Logger.log("Không tìm thấy danh mục: " + sheetCategory);
      return;
    }
    
    if (col < 3) {
      Logger.log("Không xác định được cột ngày");
      return;
    }
    
    // Đọc giá trị hiện tại và cộng thêm
    var currentVal = sheet.getRange(row, col).getValue();
    var newVal = (Number(currentVal) || 0) + Number(amount);
    sheet.getRange(row, col).setValue(newVal);
    
    // === LEVEL 8: INVENTORY LOGIC ===
    try {
      var props = PropertiesService.getScriptProperties();
      var currentInventory = parseFloat(props.getProperty("INVENTORY_VALUE") || "0");
      var updated = false;
      
      // 1. Nhập hàng (Chi Kinh Doanh) -> Tăng Tồn Kho
      // Tìm key trong map để check isBusiness
      var catKeys = Object.keys(CATEGORY_MAP);
      for (var i = 0; i < catKeys.length; i++) {
        var k = catKeys[i];
        if (CATEGORY_MAP[k].botCategory === category && CATEGORY_MAP[k].isBusiness && type === "Chi") {
           currentInventory += Number(amount);
           updated = true;
           Logger.log("📦 INV UP (" + category + "): +" + formatMoney(amount));
           break;
        }
      }
      
      if (category === "Bán hàng" && type === "Thu") {
         var cogs = Number(amount) * (1 - BUSINESS.profitMargin);
         currentInventory -= cogs;
         updated = true;
         Logger.log("📦 INV DOWN (COGS): -" + formatMoney(cogs));
      }
      
      if (updated) {
        props.setProperty("INVENTORY_VALUE", String(currentInventory));
      }
    } catch (e) {
      Logger.log("Inventory update error: " + e);
    }
    // === END LEVEL 8 ===
    
    // Gamification
    recordTransaction();
    
    return "Đã ghi nhận: " + category + " " + formatMoney(amount);
  } catch (error) {
    Logger.log("logTransaction error: " + error.toString());
    return -1;
  }
}


/**
 * Lấy tổng hợp thu/chi trong ngày
 * Đọc từ tab tháng hiện tại, cột ngày hôm nay
 */
function getDailySummary(date) {
  try {
    var sheet = getMonthSheet();
    if (!sheet) {
      return { totalIncome: 0, totalExpense: 0, netCash: 0, transactions: [], count: 0 };
    }
    
    var col = findTodayColumn(sheet);
    if (col < 3) {
      return { totalIncome: 0, totalExpense: 0, netCash: 0, transactions: [], count: 0 };
    }
    
    var lastRow = sheet.getLastRow();
    var data = sheet.getRange(1, 1, lastRow, col).getValues();
    
    var totalIncome = 0;
    var totalExpense = 0;
    var totalBusinessExpense = 0;
    var transactions = [];
    
    for (var i = 1; i < data.length; i++) { // Bỏ qua header
      var categoryName = String(data[i][0]).toUpperCase().trim();
      var dailyAmount = Number(data[i][col - 1]) || 0;
      
      if (dailyAmount === 0 || !categoryName) continue;
      
      // Bỏ qua hàng tổng hợp
      if (categoryName === "TỔNG CHI" || categoryName === "LỢI NHUẬN" || categoryName === "CUỐI NGÀY") continue;
      
      var catInfo = CATEGORY_MAP[categoryName];
      if (!catInfo) continue;
      
      if (catInfo.isBusiness) {
         totalBusinessExpense += dailyAmount;
         // KHÔNG cộng vào totalExpense cá nhân?
         // QUYẾT ĐỊNH: Tách riêng. Total Expense chỉ tính cá nhân.
      } else {
         if (catInfo.type === "Thu") {
           totalIncome += dailyAmount;
         } else {
           totalExpense += dailyAmount;
         }
      }
      
      transactions.push({
        time: "",
        content: catInfo.botCategory,
        amount: dailyAmount,
        type: catInfo.type,
        category: catInfo.botCategory
      });
    }
    
    return {
      totalIncome: totalIncome,
      totalExpense: totalExpense,
      totalBusinessExpense: totalBusinessExpense,
      netCash: totalIncome - totalExpense - totalBusinessExpense, // Net Cash vẫn trừ business expense (dòng tiền ra)
      transactions: transactions,
      count: transactions.length
    };
  } catch (e) {
    Logger.log("getDailySummary error: " + e.toString());
    return { totalIncome: 0, totalExpense: 0, netCash: 0, transactions: [], count: 0 };
  }
}

/**
 * Lấy tổng hợp thu/chi trong tháng
 * Đọc từ cột B (tổng tháng) của tab tháng hiện tại
 */
function getMonthlySummary() {
  try {
    var sheet = getMonthSheet();
    if (!sheet) {
      return { totalIncome: 0, totalExpense: 0, netCash: 0, daysWithData: 0, avgDailyIncome: 0, categoryBreakdown: {} };
    }
    
    var lastRow = sheet.getLastRow();
    var data = sheet.getRange(1, 1, lastRow, 2).getValues(); // Cột A + B
    
    var totalIncome = 0;
    var totalExpense = 0;
    var totalBusinessExpense = 0;
    var categoryBreakdown = {};
    var now = new Date();
    var daysWithData = parseInt(Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "d")); // Số ngày đã qua trong tháng (Hanoi Time)
    
    for (var i = 1; i < data.length; i++) {
      var categoryName = String(data[i][0]).toUpperCase().trim();
      var monthlyTotal = Number(data[i][1]) || 0;
      
      if (monthlyTotal === 0 || !categoryName) continue;
      
      // Bỏ qua hàng tổng hợp
      if (categoryName === "TỔNG CHI" || categoryName === "LỢI NHUẬN" || categoryName === "CUỐI NGÀY") continue;
      
      var catInfo = CATEGORY_MAP[categoryName];
      if (!catInfo) continue;
      
      if (catInfo.isBusiness) {
         totalBusinessExpense += monthlyTotal;
      } else {
         if (catInfo.type === "Thu") {
           totalIncome += monthlyTotal;
         } else {
           totalExpense += monthlyTotal; // Personal Expense
         }
      }
      
      categoryBreakdown[catInfo.botCategory] = (categoryBreakdown[catInfo.botCategory] || 0) + monthlyTotal;
    }
    
    return {
      totalIncome: totalIncome,
      totalExpense: totalExpense,
      totalBusinessExpense: totalBusinessExpense,
      netCash: totalIncome - totalExpense - totalBusinessExpense,
      daysWithData: daysWithData,
      avgDailyIncome: daysWithData > 0 ? Math.round(totalIncome / daysWithData) : 0,
      categoryBreakdown: categoryBreakdown
    };
  } catch (e) {
    Logger.log("getMonthlySummary error: " + e.toString());
    return { totalIncome: 0, totalExpense: 0, totalBusinessExpense: 0, netCash: 0, daysWithData: 0, avgDailyIncome: 0, categoryBreakdown: {} };
  }
}

/**
 * Lấy chi tiêu theo danh mục trong tháng
 * @param {string} category - Tên danh mục bot (VD: "Cafe")
 * @returns {number} - Tổng chi tiêu cho danh mục đó
 */
function getCategorySpending(category) {
  var summary = getMonthlySummary();
  return summary.categoryBreakdown[category] || 0;
}

/**
 * Lấy tổng hợp tháng trước để so sánh
 */
function getPreviousMonthSummary() {
  try {
    var now = new Date();
    var currentMonth = parseInt(Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "M"));
    var currentYear = parseInt(Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "yyyy"));
    
    var prevMonth = currentMonth - 1;
    var prevYear = currentYear;
    
    if (prevMonth === 0) {
      prevMonth = 12;
      prevYear--;
    }
    var tabName = ("0" + prevMonth).slice(-2) + "-" + prevYear;
    
    var ss = getSpreadsheet();
    var sheet = ss.getSheetByName(tabName);
    if (!sheet) return null;
    
    var lastRow = sheet.getLastRow();
    var data = sheet.getRange(1, 1, lastRow, 2).getValues();
    
    var totalIncome = 0;
    var totalExpense = 0;
    var categoryBreakdown = {};
    
    for (var i = 1; i < data.length; i++) {
      var categoryName = String(data[i][0]).toUpperCase().trim();
      var monthlyTotal = Number(data[i][1]) || 0;
      if (monthlyTotal === 0 || !categoryName) continue;
      if (categoryName === "TỔNG CHI" || categoryName === "LỢI NHUẬN" || categoryName === "CUỐI NGÀY") continue;
      
      var catInfo = CATEGORY_MAP[categoryName];
      if (!catInfo) continue;
      
      if (catInfo.type === "Thu") totalIncome += monthlyTotal;
      else totalExpense += monthlyTotal;
      
      categoryBreakdown[catInfo.botCategory] = (categoryBreakdown[catInfo.botCategory] || 0) + monthlyTotal;
    }
    
    return {
      tabName: tabName,
      totalIncome: totalIncome,
      totalExpense: totalExpense,
      netCash: totalIncome - totalExpense,
      categoryBreakdown: categoryBreakdown
    };
  } catch (e) {
    Logger.log("getPreviousMonthSummary error: " + e.toString());
    return null;
  }
}

/**
 * Lấy xu hướng chi tiêu 3-5 tháng gần nhất
 */
function getMultiMonthTrend() {
  try {
    var ss = getSpreadsheet();
    var now = new Date();
    var months = [];
    
    var currentMonth = parseInt(Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "M"));
    var currentYear = parseInt(Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "yyyy"));
    
    for (var m = 0; m < 5; m++) {
      var targetMonth = currentMonth - m;
      var targetYear = currentYear;
      while (targetMonth <= 0) {
        targetMonth += 12;
        targetYear--;
      }
      var tabName = ("0" + targetMonth).slice(-2) + "-" + targetYear;
      var sheet = ss.getSheetByName(tabName);
      
      if (!sheet) continue;
      
      var lastRow = sheet.getLastRow();
      var data = sheet.getRange(1, 1, lastRow, 2).getValues();
      
      var totalIncome = 0;
      var totalExpense = 0;
      var cats = {};
      
      for (var i = 1; i < data.length; i++) {
        var catName = String(data[i][0]).toUpperCase().trim();
        var val = Number(data[i][1]) || 0;
        if (val === 0 || !catName) continue;
        if (catName === "TỔNG CHI" || catName === "LỢI NHUẬN" || catName === "CUỐI NGÀY") continue;
        
        var catInfo = CATEGORY_MAP[catName];
        if (!catInfo) continue;
        
        if (catInfo.type === "Thu") totalIncome += val;
        else totalExpense += val;
        cats[catInfo.botCategory] = (cats[catInfo.botCategory] || 0) + val;
      }
      
      months.push({
        tab: tabName,
        income: totalIncome,
        expense: totalExpense,
        net: totalIncome - totalExpense,
        categories: cats
      });
    }
    
    return months;
  } catch (e) {
    Logger.log("getMultiMonthTrend error: " + e.toString());
    return [];
  }
}

/**
 * Lấy số dư tài khoản từ tab CASH FLOW
 */
function getAccountBalances() {
  try {
    var ss = getSpreadsheet();
    var sheet = ss.getSheetByName("CASH FLOW");
    if (!sheet) return null;
    
    var lastRow = sheet.getLastRow();
    var lastCol = sheet.getLastColumn();
    var data = sheet.getRange(1, 1, lastRow, lastCol).getValues();
    
    var balances = [];
    var totalBalance = 0;
    
    // Tìm cột SỐ DƯ TK (thường ở phía bên phải)
    for (var i = 0; i < data.length; i++) {
      for (var j = 0; j < data[i].length; j++) {
        var cellText = String(data[i][j]).toUpperCase().trim();
        if (cellText === "SỐ DƯ TK" || cellText === "SỐ DƯ") {
          // Đọc các dòng phía dưới cùng cột
          for (var k = i + 1; k < data.length; k++) {
            var bankName = String(data[k][j]).trim();
            var amount = Number(data[k][j + 1]) || 0;
            if (!bankName || bankName === "") continue;
            if (bankName.toUpperCase() === "TỔNG" || bankName.toUpperCase().indexOf("TỔNG") >= 0) {
              totalBalance = amount;
              continue;
            }
            if (amount > 0 || bankName.length > 0) {
              balances.push({name: bankName, amount: amount});
            }
          }
          break;
        }
      }
      if (balances.length > 0) break;
    }
    
    // Nếu không tìm được cấu trúc SỐ DƯ TK, đọc tổng quát
    if (balances.length === 0) {
      // Fallback: đọc tất cả dòng có tên ngân hàng
      var bankNames = ["VP BANK", "TECH", "SHOPEE", "MOMO", "VIB", "TP", "KIOTVIET", "OREKA", "TIKTOK", "CASH"];
      for (var bi = 0; bi < data.length; bi++) {
        for (var bj = 0; bj < data[bi].length; bj++) {
          var cellVal = String(data[bi][bj]).toUpperCase().trim();
          for (var bn = 0; bn < bankNames.length; bn++) {
            if (cellVal === bankNames[bn]) {
              var bankAmount = Number(data[bi][bj + 1]) || 0;
              balances.push({name: data[bi][bj], amount: bankAmount});
              totalBalance += bankAmount;
            }
          }
        }
      }
    }
    
    return {
      balances: balances,
      total: totalBalance
    };
  } catch (e) {
    Logger.log("getAccountBalances error: " + e.toString());
    return null;
  }
}

/**
 * Kiểm tra budget và gửi cảnh báo tự động
 * Chạy tự động hàng ngày qua trigger
 */
function checkBudgetAlerts() {
  var monthly = getMonthlySummary();
  var alerts = [];
  var now = new Date();
  var dayOfMonth = parseInt(Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "d")); // Hanoi time
  
  // 1. Cảnh báo Cafe
  var cafeSpending = monthly.categoryBreakdown["Cafe"] || 0;
  var cafeBudgetMonth = ALERTS.cafeBudgetWeekly * 4;
  var cafePercent = Math.round(cafeSpending / cafeBudgetMonth * 100);
  if (cafePercent > 80) {
    alerts.push("☕ Cafe: " + formatMoney(cafeSpending) + "/" + formatMoney(cafeBudgetMonth) + " (" + cafePercent + "% budget)");
  }
  
  // 2. Cảnh báo Phụ phí
  var miscSpending = monthly.categoryBreakdown["Phụ phí"] || 0;
  var miscPercent = Math.round(miscSpending / ALERTS.miscBudgetMonthly * 100);
  if (miscPercent > 80) {
    alerts.push("⚠️ Phụ phí: " + formatMoney(miscSpending) + "/" + formatMoney(ALERTS.miscBudgetMonthly) + " (" + miscPercent + "% budget)");
  }
  
  // 3. Cảnh báo tổng chi vượt tổng thu
  if (monthly.totalExpense > monthly.totalIncome && monthly.totalIncome > 0) {
    alerts.push("🔴 CHI > THU: Chi " + formatMoney(monthly.totalExpense) + " > Thu " + formatMoney(monthly.totalIncome));
  }
  
  // 4. Kiểm tra nợ sắp đến hạn
  var upcomingPayments = getNextPayment();
  upcomingPayments.forEach(function(p) {
    if (p.daysLeft <= 3 && p.daysLeft >= 0) {
      alerts.push("🚨 " + p.name + ": " + formatMoney(p.amount) + " - còn " + p.daysLeft + " ngày!");
    }
  });
  
  if (alerts.length > 0) {
    var lines = [];
    lines.push("🔔 CẢNH BÁO TÀI CHÍNH (" + Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "dd/MM") + ")");
    lines.push("━━━━━━━━━━━━━━━━━━━━");
    lines.push("");
    alerts.forEach(function(a) { lines.push(a); });
    sendMessage(OWNER_CHAT_ID, lines.join("\n"));
  }
}

/**
 * ============================================================
 * LEVEL 2 FEATURES - Nâng cấp trung bình
 * ============================================================
 */

/**
 * DỰ BÁO DÒNG TIỀN cuối tháng
 * Dựa trên data hiện tại + lịch sử để predict
 */
function getCashFlowForecast() {
  try {
    var monthly = getMonthlySummary();
    var now = new Date();
    var todayStr = Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "d");
    var today = parseInt(todayStr); // Ngày hiện tại theo giờ VN
    var monthStr = Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "M");
    var yearStr = Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "yyyy");
    var daysInMonth = new Date(parseInt(yearStr), parseInt(monthStr), 0).getDate();
    var daysLeft = daysInMonth - today;
    
    // Doanh thu dự kiến cuối tháng
    var avgDailyIncome = monthly.avgDailyIncome || 0;
    var projectedIncome = monthly.totalIncome + (avgDailyIncome * daysLeft);
    
    // Chi tiêu dự kiến (dựa trên tốc độ chi hiện tại)
    var avgDailyExpense = today > 0 ? Math.round(monthly.totalExpense / today) : 0;
    var projectedExpense = monthly.totalExpense + (avgDailyExpense * daysLeft);
    
    // Chi phí cố định còn phải trả trong tháng
    var fixedCostsRemaining = 0;
    DEBTS.forEach(function(d) {
      if (d.payDay && d.payDay > today && d.monthlyPayment > 0) {
        fixedCostsRemaining += d.monthlyPayment;
      }
    });
    
    // Lấy số dư hiện tại
    var balanceData = getAccountBalances();
    var currentBalance = balanceData ? balanceData.total : 0;
    
    // Dự báo số dư cuối tháng
    var projectedNet = projectedIncome - projectedExpense;
    var projectedEndBalance = currentBalance + (projectedIncome - monthly.totalIncome) - (projectedExpense - monthly.totalExpense) - fixedCostsRemaining;
    
    // Trend từ tháng trước
    var prevMonth = getPreviousMonthSummary();
    var incomeVsPrev = prevMonth ? projectedIncome - prevMonth.totalIncome : 0;
    
    return {
      today: today,
      daysLeft: daysLeft,
      daysInMonth: daysInMonth,
      currentIncome: monthly.totalIncome,
      currentExpense: monthly.totalExpense,
      avgDailyIncome: avgDailyIncome,
      avgDailyExpense: avgDailyExpense,
      projectedIncome: projectedIncome,
      projectedExpense: projectedExpense,
      projectedNet: projectedNet,
      fixedCostsRemaining: fixedCostsRemaining,
      currentBalance: currentBalance,
      projectedEndBalance: projectedEndBalance,
      incomeVsPrev: incomeVsPrev,
      prevMonthIncome: prevMonth ? prevMonth.totalIncome : 0
    };
  } catch (e) {
    Logger.log("getCashFlowForecast error: " + e.toString());
    return null;
  }
}

/**
 * MỤC TIÊU - Lưu/đọc mục tiêu chi tiêu
 */
function getGoals() {
  try {
    var props = PropertiesService.getScriptProperties();
    var goalsJson = props.getProperty("spending_goals");
    return goalsJson ? JSON.parse(goalsJson) : [];
  } catch (e) {
    return [];
  }
}

function setGoal(category, monthlyLimit, label) {
  var goals = getGoals();
  // Tìm và cập nhật goal cũ hoặc thêm mới
  var found = false;
  for (var i = 0; i < goals.length; i++) {
    if (goals[i].category === category) {
      goals[i].limit = monthlyLimit;
      goals[i].label = label || category;
      found = true;
      break;
    }
  }
  if (!found) {
    goals.push({category: category, limit: monthlyLimit, label: label || category});
  }
  PropertiesService.getScriptProperties().setProperty("spending_goals", JSON.stringify(goals));
  return goals;
}

function removeGoal(category) {
  var goals = getGoals();
  goals = goals.filter(function(g) { return g.category !== category; });
  PropertiesService.getScriptProperties().setProperty("spending_goals", JSON.stringify(goals));
  return goals;
}

function checkGoalProgress() {
  var goals = getGoals();
  if (goals.length === 0) return [];
  
  var monthly = getMonthlySummary();
  var now = new Date();
  var todayStr = Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "d");
  var today = parseInt(todayStr);
  var monthStr = Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "M");
  var yearStr = Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "yyyy");
  var daysInMonth = new Date(parseInt(yearStr), parseInt(monthStr), 0).getDate();
  
  var results = [];
  goals.forEach(function(goal) {
    var spent = monthly.categoryBreakdown[goal.category] || 0;
    var percent = goal.limit > 0 ? Math.round(spent / goal.limit * 100) : 0;
    var dayPercent = Math.round(today / daysInMonth * 100);
    var status = "🟢";
    if (percent > dayPercent + 10) status = "🟡";
    if (percent > 90) status = "🔴";
    if (percent >= 100) status = "❌";
    
    results.push({
      label: goal.label,
      category: goal.category,
      spent: spent,
      limit: goal.limit,
      percent: percent,
      status: status,
      remaining: Math.max(0, goal.limit - spent)
    });
  });
  
  return results;
}

/**
 * LƯƠNG NHÂN VIÊN - Đọc từ tab tháng
 */
function getEmployeeSalaries() {
  try {
    var sheet = getMonthSheet();
    if (!sheet) return null;
    
    var lastRow = sheet.getLastRow();
    var lastCol = sheet.getLastColumn();
    var data = sheet.getRange(1, 1, lastRow, lastCol).getValues();
    
    var employeeNames = ["VY", "LY", "LINH", "QUỲNH"];
    var employees = [];
    var totalSalary = 0;
    
    for (var i = 1; i < data.length; i++) {
      var catName = String(data[i][0]).toUpperCase().trim();
      if (employeeNames.indexOf(catName) >= 0) {
        var monthlyTotal = Number(data[i][1]) || 0;
        
        // Lấy chi tiết từng ngày
        var dailyPayments = [];
        for (var col = 2; col < data[i].length; col++) {
          var val = Number(data[i][col]) || 0;
          if (val > 0) {
            dailyPayments.push({day: col - 1, amount: val});
          }
        }
        
        employees.push({
          name: catName,
          total: monthlyTotal,
          payments: dailyPayments
        });
        totalSalary += monthlyTotal;
      }
    }
    
    return {employees: employees, total: totalSalary};
  } catch (e) {
    Logger.log("getEmployeeSalaries error: " + e.toString());
    return null;
  }
}

/**
 * XOÁ GIAO DỊCH - Trừ tiền từ ô hiện tại
 */
function undoTransaction(category, amount) {
  try {
    var sheet = getMonthSheet();
    if (!sheet) return {success: false, message: "Không tìm thấy tab tháng"};
    
    var sheetCategory = BOT_TO_SHEET[category] || category.toUpperCase();
    var row = findCategoryRow(sheet, sheetCategory);
    var col = findTodayColumn(sheet);
    
    if (row === -1) return {success: false, message: "Không tìm thấy danh mục: " + category};
    if (col < 3) return {success: false, message: "Lỗi xác định cột ngày"};
    
    var currentValue = Number(sheet.getRange(row, col).getValue()) || 0;
    
    if (amount > currentValue) {
      return {success: false, message: "Số tiền xoá (" + formatMoney(amount) + ") lớn hơn giá trị hiện tại (" + formatMoney(currentValue) + ")"};
    }
    
    sheet.getRange(row, col).setValue(currentValue - amount);
    
    return {
      success: true, 
      message: "Đã xoá " + formatMoney(amount) + " từ " + category + " (còn lại: " + formatMoney(currentValue - amount) + ")"
    };
  } catch (e) {
    return {success: false, message: "Lỗi: " + e.toString()};
  }
}

/**
 * BIỂU ĐỒ - Tạo URL Google Charts
 */
function getSpendingChartUrl() {
  var monthly = getMonthlySummary();
  var cats = monthly.categoryBreakdown;
  
  if (!cats || Object.keys(cats).length === 0) return null;
  
  var labels = [];
  var values = [];
  
  Object.keys(cats).forEach(function(cat) {
    if (cats[cat] > 0) {
      labels.push(cat);
      values.push(cats[cat]);
    }
  });
  
  // Google Charts API - Pie chart
  var chartData = "t:" + values.join(",");
  var chartLabels = labels.map(function(l, i) { return l + " " + formatMoney(values[i]); }).join("|");
  
  var url = "https://chart.googleapis.com/chart?" +
    "cht=p3" +
    "&chs=600x400" +
    "&chd=" + chartData +
    "&chl=" + encodeURIComponent(chartLabels) +
    "&chtt=" + encodeURIComponent("Chi tiêu tháng " + (new Date().getMonth() + 1)) +
    "&chco=FF6384,36A2EB,FFCE56,4BC0C0,9966FF,FF9F40,FF6384,C9CBCF";
  
  return url;
}

function getIncomeExpenseChartUrl() {
  var months = getMultiMonthTrend();
  if (months.length < 2) return null;
  
  months.reverse(); // Cũ → mới
  
  var labels = months.map(function(m) { return m.tab; }).join("|");
  var incomeData = months.map(function(m) { return m.income; }).join(",");
  var expenseData = months.map(function(m) { return m.expense; }).join(",");
  var maxVal = Math.max.apply(null, months.map(function(m) { return Math.max(m.income, m.expense); }));
  
  var url = "https://chart.googleapis.com/chart?" +
    "cht=bvg" +
    "&chs=600x400" +
    "&chd=t:" + incomeData + "|" + expenseData +
    "&chdl=" + encodeURIComponent("Thu|Chi") +
    "&chxl=0:|" + encodeURIComponent(labels) +
    "&chxt=x,y" +
    "&chds=0," + maxVal +
    "&chtt=" + encodeURIComponent("Thu vs Chi theo tháng") +
    "&chco=4BC0C0,FF6384";
  
  return url;
}

/**
 * ============================================================
 * CASH FLOW ENGINE - Tính toán dòng tiền & dự báo
 * ============================================================
 */

/**
 * Tính số tiền mặt cần chuẩn bị cho một ngày cụ thể trong tháng
 * Tính lũy kế: từ đầu tháng đến ngày đó cần có bao nhiêu tiền
 * @param {number} dayOfMonth - Ngày trong tháng (1-31)
 * @returns {Object} - Chi tiết tiền cần chuẩn bị
 */
function calculateCumulativeCashNeeded(dayOfMonth) {
  var cashNeeded = 0;
  var breakdown = [];
  
  // Tính các khoản nợ đến hạn từ đầu tháng đến ngày dayOfMonth
  DEBTS.forEach(function(debt) {
    if (debt.payDay && debt.payDay <= dayOfMonth && debt.monthlyPayment > 0) {
      cashNeeded += debt.monthlyPayment;
      breakdown.push({
        name: debt.fullName,
        amount: debt.monthlyPayment,
        dueDay: debt.payDay,
        status: "Đã qua hạn hoặc đúng hạn"
      });
    }
  });
  
  // Tính tiền nhà (chia đều 200k/ngày, tích lũy đến ngày dayOfMonth)
  var rentAccumulation = RENT.dailySaving * dayOfMonth;
  cashNeeded += rentAccumulation;
  
  // Chi phí sinh hoạt cơ bản (ước tính 117k/ngày = 3.5tr/30 ngày)
  var dailyLiving = 117000;
  var livingCost = dailyLiving * dayOfMonth;
  cashNeeded += livingCost;
  
  return {
    totalCashNeeded: cashNeeded,
    debtPayments: breakdown,
    rentAccumulation: rentAccumulation,
    livingCost: livingCost,
    dayOfMonth: dayOfMonth
  };
}

/**
 * Tính số tiền mặt cần có sẵn vào ngày 1 hàng tháng
 * (Để đảm bảo đủ tiền trước mốc TCB ngày 5)
 * @returns {Object}
 */
function getFirstOfMonthTarget() {
  // Cần đủ tiền TCB (1tr ngày 5) + sinh hoạt 5 ngày + tích lũy nhà 5 ngày
  var tcbPayment = 1000000;
  var livingFor5Days = 117000 * 5;
  var rentFor5Days = RENT.dailySaving * 5;
  
  return {
    total: tcbPayment + livingFor5Days + rentFor5Days,
    breakdown: {
      "TCB (ngày 5)": tcbPayment,
      "Sinh hoạt 5 ngày": livingFor5Days,
      "Tích lũy nhà 5 ngày": rentFor5Days
    }
  };
}

/**
 * Lấy thông tin khoản thanh toán tiếp theo
 * @returns {Object} - {name, amount, daysLeft, dueDate}
 */
function getNextPayment() {
  var now = new Date();
  var today = now.getDate();
  var currentMonth = now.getMonth();
  var currentYear = now.getFullYear();
  
  var upcomingPayments = [];
  
  // Kiểm tra các khoản nợ
  DEBTS.forEach(function(debt) {
    if (debt.payDay && debt.monthlyPayment > 0) {
      var dueDay = debt.payDay;
      var daysLeft;
      var dueDate;
      
      if (dueDay > today) {
        daysLeft = dueDay - today;
        dueDate = new Date(currentYear, currentMonth, dueDay);
      } else if (dueDay === today) {
        daysLeft = 0;
        dueDate = new Date(currentYear, currentMonth, dueDay);
      } else {
        // Đã qua ngày trả trong tháng này → tính cho tháng sau
        daysLeft = (new Date(currentYear, currentMonth + 1, dueDay) - now) / (1000 * 60 * 60 * 24);
        dueDate = new Date(currentYear, currentMonth + 1, dueDay);
      }
      
      upcomingPayments.push({
        name: debt.fullName,
        shortName: debt.name,
        amount: debt.monthlyPayment,
        daysLeft: Math.ceil(daysLeft),
        dueDate: dueDate
      });
    }
  });
  
  // Kiểm tra tiền nhà
  RENT.nextPayDates.forEach(function(dateStr) {
    var rentDate = new Date(dateStr);
    var daysLeft = Math.ceil((rentDate - now) / (1000 * 60 * 60 * 24));
    if (daysLeft >= 0 && daysLeft <= 90) {
      upcomingPayments.push({
        name: "Tiền nhà",
        shortName: "RENT",
        amount: RENT.amount,
        daysLeft: daysLeft,
        dueDate: rentDate
      });
    }
  });
  
  // Sắp xếp theo ngày gần nhất
  upcomingPayments.sort(function(a, b) { return a.daysLeft - b.daysLeft; });
  
  return upcomingPayments;
}

/**
 * Kiểm tra nguy cơ gãy dòng tiền
 * Dựa trên doanh thu hiện tại vs các mốc thanh toán sắp tới
 * @returns {Object} - {isAtRisk, riskLevel, message, details}
 */
function checkCashFlowRisk() {
  var monthlySummary = getMonthlySummary();
  var now = new Date();
  var todayStr = Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "d");
  var today = parseInt(todayStr); // Ngày hiện tại theo giờ VN
  
  // Tính số ngày trong tháng (dựa trên tháng/năm VN)
  var monthStr = Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "M");
  var yearStr = Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "yyyy");
  var daysInMonth = new Date(parseInt(yearStr), parseInt(monthStr), 0).getDate(); // Trick: day 0 of next month = last day of current month
  
  var daysLeft = daysInMonth - today;
  
  // Tính lợi nhuận thực tế (60% doanh thu)
  var actualProfit = monthlySummary.totalIncome * BUSINESS.profitMargin;
  var projectedMonthlyProfit = monthlySummary.daysWithData > 0 
    ? (actualProfit / monthlySummary.daysWithData) * daysInMonth 
    : 0;
  
  // Tính tổng chi phí cố định trong tháng
  var totalFixedCost = TOTAL_MONTHLY_DEBT_PAYMENT + (RENT.amount / RENT.cycleMonths) + 3500000; // 3.5tr sinh hoạt
  
  var gap = projectedMonthlyProfit + BUSINESS.monthlyShareOffice - totalFixedCost;
  
  var riskLevel, message;
  
  if (gap >= 3000000) {
    riskLevel = "🟢 AN TOÀN";
    message = "Dòng tiền ổn định. Dư " + formatMoney(gap) + " để trả thêm gốc nợ.";
  } else if (gap >= 0) {
    riskLevel = "🟡 SÁT NÚT";
    message = "Chỉ dư " + formatMoney(gap) + ". Cắt giảm cafe/phụ phí ngay!";
  } else {
    riskLevel = "🔴 NGUY HIỂM";
    message = "Thiếu " + formatMoney(Math.abs(gap)) + "! Cần tăng doanh thu hoặc vay tạm để không bị nợ xấu.";
  }
  
  return {
    isAtRisk: gap < 0,
    riskLevel: riskLevel,
    message: message,
    projectedProfit: projectedMonthlyProfit,
    totalFixedCost: totalFixedCost,
    gap: gap,
    avgDailyRevenue: monthlySummary.avgDailyIncome
  };
}

/**
 * Tính tiến độ tích lũy tiền nhà
 * @returns {Object} - {nextRentDate, daysLeft, amountNeeded, amountSaved, dailySavingNeeded, progress}
 */
function getRentProgress() {
  var now = new Date();
  var nextRentDate = null;
  var daysLeft = 0;
  
  // Tìm mốc tiền nhà tiếp theo
  for (var i = 0; i < RENT.nextPayDates.length; i++) {
    var rentDate = new Date(RENT.nextPayDates[i]);
    if (rentDate > now) {
      nextRentDate = rentDate;
      daysLeft = Math.ceil((rentDate - now) / (1000 * 60 * 60 * 24));
      break;
    }
  }
  
  if (!nextRentDate) {
    return { message: "Không tìm thấy mốc tiền nhà tiếp theo. Hãy cập nhật RENT.nextPayDates." };
  }
  
  // Tính số tiền đã tích lũy dựa trên ngày hiện tại
  // (Giả sử tích lũy đều từ mốc trước đó)
  var dailySavingNeeded = Math.ceil(RENT.amount / daysLeft);
  var progress = Math.round((1 - (daysLeft * dailySavingNeeded / RENT.amount)) * 100);
  
  return {
    nextRentDate: Utilities.formatDate(nextRentDate, "Asia/Ho_Chi_Minh", "dd/MM/yyyy"),
    daysLeft: daysLeft,
    amountNeeded: RENT.amount,
    dailySavingNeeded: dailySavingNeeded,
    progress: Math.max(0, Math.min(100, progress))
  };
}

/**
 * Tạo bảng tổng hợp nợ với thông tin chi tiết
 * @returns {string} - Bảng nợ dạng text
 */
function getDebtSummary() {
  var totalDebt = 0;
  var totalMonthlyInterest = 0;
  var totalMonthlyPayment = 0;
  var lines = [];
  
  lines.push("📊 BẢNG TỔNG HỢP NỢ");
  lines.push("━━━━━━━━━━━━━━━━━━━━");
  
  DEBTS.forEach(function(debt) {
    totalDebt += debt.balance;
    var monthlyInterest = Math.round(debt.balance * debt.monthlyRate);
    totalMonthlyInterest += monthlyInterest;
    totalMonthlyPayment += debt.monthlyPayment;
    
    var icon = debt.type === "personal" ? "👤" : "🏦";
    var status = "";
    if (debt.payDay) {
      var now = new Date();
      var todayStr = Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "d");
      var today = parseInt(todayStr);
      var daysLeft = debt.payDay > today ? debt.payDay - today : debt.payDay + 30 - today;
      status = " (còn " + daysLeft + " ngày)";
    }
    
    lines.push("");
    lines.push(icon + " " + debt.fullName + status);
    lines.push("   Dư nợ: " + formatMoney(debt.balance));
    if (debt.monthlyRate > 0) {
      lines.push("   Lãi/tháng: " + formatMoney(monthlyInterest) + " (" + (debt.monthlyRate * 100) + "%)");
    }
    if (debt.monthlyPayment > 0) {
      lines.push("   Trả/tháng: " + formatMoney(debt.monthlyPayment) + " (ngày " + debt.payDay + ")");
    }
  });
  
  lines.push("");
  lines.push("━━━━━━━━━━━━━━━━━━━━");
  lines.push("💰 Tổng nợ: " + formatMoney(totalDebt));
  lines.push("💸 Tổng lãi/tháng: " + formatMoney(totalMonthlyInterest));
  lines.push("📅 Tổng trả/tháng: " + formatMoney(totalMonthlyPayment));
  
  return lines.join("\n");
}

/**
 * Format số tiền thành dạng đọc được
 * @param {number} amount
 * @returns {string}
 */
function formatMoney(amount) {
  if (amount >= 1000000) {
    var millions = Math.round(amount / 100000) / 10;
    return millions + "tr";
  } else if (amount >= 1000) {
    return Math.round(amount / 1000) + "k";
  }
  return amount + "đ";
}

/**
 * Format số tiền đầy đủ với dấu phẩy
 * @param {number} amount
 * @returns {string}
 */
function formatMoneyFull(amount) {
  return amount.toLocaleString("vi-VN") + "đ";
}
/**
 * ============================================================
 * TELEGRAM SERVICE - Gửi/nhận tin nhắn Telegram
 * ============================================================
 */

/**
 * Gửi tin nhắn text qua Telegram
 * @param {string} chatId - Chat ID người nhận
 * @param {string} text - Nội dung tin nhắn
 * @param {string} parseMode - "Markdown" hoặc "HTML" (mặc định: Markdown)
 */
function sendMessage(chatId, text, parseMode) {
  var url = "https://api.telegram.org/bot" + TELEGRAM_TOKEN + "/sendMessage";
  
  // Mặc định không dùng Markdown để tránh lỗi formatting
  var payload = {
    "chat_id": chatId,
    "text": text
  };
  
  var options = {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };
  
  try {
    var response = UrlFetchApp.fetch(url, options);
    var result = JSON.parse(response.getContentText());
    
    if (!result.ok) {
      Logger.log("Telegram send error: " + response.getContentText());
    }
  } catch (error) {
    Logger.log("Telegram API error: " + error.toString());
  }
}

/**
 * Gửi nhắc nhở buổi sáng (8h mỗi ngày)
 * Thiết lập trigger: Triggers > Add Trigger > sendDailyReminder > Time-driven > Day timer > 8am-9am
 */
function sendDailyReminder() {
  var now = new Date();
  var today = Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "d");
  var month = Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "M");
  
  var lines = [];
  lines.push("☀️ *NHẮC NHỞ SÁNG " + today + "/" + month + "*");
  lines.push("━━━━━━━━━━━━━━━━━━━━");
  
  // 1. Các mốc thanh toán sắp tới
  var upcomingPayments = getNextPayment();
  var urgentPayments = upcomingPayments.filter(function(p) { return p.daysLeft <= 7; });
  
  if (urgentPayments.length > 0) {
    lines.push("");
    lines.push("⚠️ *SẮP ĐẾN HẠN:*");
    urgentPayments.forEach(function(p) {
      var urgency = p.daysLeft === 0 ? "🚨 HÔM NAY!" : "⏰ Còn " + p.daysLeft + " ngày";
      lines.push("• " + p.name + ": " + formatMoney(p.amount) + " - " + urgency);
    });
  }
  
  // 2. Mục tiêu hôm nay
  lines.push("");
  lines.push("🎯 *MỤC TIÊU HÔM NAY:*");
  lines.push("• Doanh thu tối thiểu: " + formatMoney(BUSINESS.targetDailyRevenue));
  lines.push("• Tích lũy tối thiểu: " + formatMoney(BUSINESS.targetDailyAccumulation));
  
  // 3. Tiến độ tiền nhà
  var rentProgress = getRentProgress();
  if (rentProgress.daysLeft) {
    lines.push("");
    lines.push("🏠 *TIỀN NHÀ:*");
    lines.push("• Mốc: " + rentProgress.nextRentDate + " (còn " + rentProgress.daysLeft + " ngày)");
    lines.push("• Cần tích lũy: " + formatMoney(rentProgress.dailySavingNeeded) + "/ngày");
  }
  
  // 4. Kiểm tra rủi ro dòng tiền
  var risk = checkCashFlowRisk();
  lines.push("");
  lines.push("📈 *TÌNH TRẠNG:* " + risk.riskLevel);
  lines.push(risk.message);
  
  lines.push("");
  lines.push("💪 Hãy bán hàng chăm chỉ hôm nay!");
  
  sendMessage(OWNER_CHAT_ID, lines.join("\n"));
}

/**
 * Gửi cảnh báo nợ trước 7 ngày
 * Thiết lập trigger: Triggers > Add Trigger > sendDebtAlert > Time-driven > Day timer > 7am-8am
 */
function sendDebtAlert() {
  var upcomingPayments = getNextPayment();
  var alertPayments = upcomingPayments.filter(function(p) { 
    return p.daysLeft === ALERTS.debtReminderDaysBefore; 
  });
  
  if (alertPayments.length === 0) return;
  
  var lines = [];
  lines.push("🔔 *CẢNH BÁO NỢ - 7 NGÀY NỮA*");
  lines.push("━━━━━━━━━━━━━━━━━━━━");
  
  alertPayments.forEach(function(p) {
    lines.push("");
    lines.push("💸 " + p.name + ": *" + formatMoney(p.amount) + "*");
    lines.push("   📅 Hạn: " + Utilities.formatDate(p.dueDate, "Asia/Ho_Chi_Minh", "dd/MM/yyyy"));
    lines.push("   ⏰ Chuẩn bị tiền NGAY!");
  });
  
  sendMessage(OWNER_CHAT_ID, lines.join("\n"));
}

/**
 * Gửi báo cáo cuối ngày (9h tối)
 * Thiết lập trigger: Triggers > Add Trigger > sendEveningReport > Time-driven > Day timer > 9pm-10pm
 */
function sendEveningReport() {
  var daily = getDailySummary();
  var monthly = getMonthlySummary();
  var now = new Date();
  
  var dailyProfit = daily.totalIncome * BUSINESS.profitMargin;
  var targetHit = dailyProfit >= BUSINESS.targetDailyAccumulation;
  
  var lines = [];
  lines.push("🌙 *BÁO CÁO CUỐI NGÀY " + Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "dd/MM") + "*");
  lines.push("━━━━━━━━━━━━━━━━━━━━");
  
  // Kết quả ngày
  lines.push("");
  lines.push("📊 *KẾT QUẢ HÔM NAY:*");
  lines.push("• Thu: +" + formatMoney(daily.totalIncome));
  lines.push("• Chi: -" + formatMoney(daily.totalExpense));
  lines.push("• Lợi nhuận (60%): " + formatMoney(dailyProfit));
  lines.push("• Mục tiêu 587k: " + (targetHit ? "✅ ĐẠT" : "❌ CHƯA ĐẠT"));
  
  // Tổng hợp tháng
  lines.push("");
  lines.push("📅 *TỔNG HỢP THÁNG:*");
  lines.push("• Tổng doanh thu: " + formatMoney(monthly.totalIncome));
  lines.push("• Tổng chi: " + formatMoney(monthly.totalExpense));
  lines.push("• TB doanh thu/ngày: " + formatMoney(monthly.avgDailyIncome));
  
  // Cảnh báo cafe/phụ phí
  var cafeSpending = getCategorySpending("Cafe");
  var miscSpending = getCategorySpending("Phụ phí");
  
  if (cafeSpending > ALERTS.cafeBudgetWeekly) {
    lines.push("");
    lines.push("☕ *CẢNH BÁO:* Tiền cafe tháng này đã " + formatMoney(cafeSpending) + "!");
  }
  if (miscSpending > ALERTS.miscBudgetMonthly) {
    lines.push("");
    lines.push("⚠️ *CẢNH BÁO:* Phụ phí tháng này đã " + formatMoney(miscSpending) + "!");
  }
  
  if (daily.count === 0) {
    lines.push("");
    lines.push("📝 Bạn chưa nhập giao dịch nào hôm nay. Đừng quên ghi chép nhé!");
  }
  
  sendMessage(OWNER_CHAT_ID, lines.join("\n"));
}

/**
 * Hàm tiện ích: Lấy Chat ID từ tin nhắn mới nhất
 * Chạy hàm này sau khi gửi /start cho bot để lấy OWNER_CHAT_ID
 */
function getUpdates() {
  var url = "https://api.telegram.org/bot" + TELEGRAM_TOKEN + "/getUpdates";
  var response = UrlFetchApp.fetch(url);
  var data = JSON.parse(response.getContentText());
  
  if (data.result && data.result.length > 0) {
    var lastMessage = data.result[data.result.length - 1];
    var chatId = lastMessage.message.chat.id;
    Logger.log("✅ CHAT ID CỦA BẠN: " + chatId);
    Logger.log("Hãy copy số này và dán vào OWNER_CHAT_ID trong Config.gs");
    return chatId;
  } else {
    Logger.log("❌ Không tìm thấy tin nhắn. Hãy gửi /start cho bot trước, rồi chạy lại hàm này.");
    return null;
  }
}
/**
 * ============================================================
 * CODE.GS - File chính: Xử lý Webhook & Điều phối
 * ============================================================
 * 
 * Chatbot Quản Lý Tài Chính Cá Nhân
 * - Nhập liệu qua Telegram
 * - Phân tích giao dịch bằng Gemini API
 * - Lưu trữ trên Google Sheets
 * - Nhắc nhở trả nợ tự động
 * - Theo dõi dòng tiền realtime
 */

/**
 * Webhook handler - Nhận tin nhắn từ Telegram
 */
// (Đã xoá Webhook handler cũ để tránh xung đột với Haravan Webhook)

/**
 * Xử lý tin nhắn thường (nhập giao dịch hoặc hỏi AI)
 */
function processMessage(chatId, userText) {
  // 1. Dùng Gemini phân tích tin nhắn
  var transaction = parseTransaction(userText);
  
  if (transaction.type === "none" || transaction.amount === 0) {
    // Không phải giao dịch → Xử lý như câu hỏi
    var daily = getDailySummary();
    var monthly = getMonthlySummary();
    var context = {
      today: {
        income: daily.totalIncome,
        expense: daily.totalExpense,
        profit: daily.totalIncome * BUSINESS.profitMargin
      },
      month: {
        income: monthly.totalIncome,
        expense: monthly.totalExpense,
        avgDailyRevenue: monthly.avgDailyIncome
      }
    };
    
    var answer = answerQuestion(userText, context);
    sendMessage(chatId, answer);
    return;
  }
  
  // 2. Ghi giao dịch vào Sheet
  logTransaction(transaction.content, transaction.amount, transaction.type, transaction.category);
  
  // 3. Tính toán tình hình sau giao dịch
  var daily = getDailySummary();
  var dailyProfit = daily.totalIncome * BUSINESS.profitMargin;
  var targetProgress = Math.round((dailyProfit / BUSINESS.targetDailyAccumulation) * 100);
  
  // 4. Tạo phản hồi
  var icon = transaction.type === "Thu" ? "💰" : "💸";
  var lines = [];
  
  lines.push(icon + " *Đã ghi nhận:* " + transaction.content);
  lines.push("📝 " + transaction.type + ": " + formatMoneyFull(transaction.amount));
  lines.push("🏷 Danh mục: " + transaction.category);
  lines.push("");
  
  // Thống kê ngày
  lines.push("📊 *Hôm nay:*");
  lines.push("• Thu: +" + formatMoney(daily.totalIncome));
  lines.push("• Chi: -" + formatMoney(daily.totalExpense));
  
  if (daily.totalIncome > 0) {
    lines.push("• Lợi nhuận (60%): " + formatMoney(dailyProfit));
    
    // Tiến độ mục tiêu 587k
    if (targetProgress >= 100) {
      lines.push("🎯 Mục tiêu 587k: ✅ ĐẠT! (" + targetProgress + "%)");
    } else {
      var remaining = BUSINESS.targetDailyAccumulation - dailyProfit;
      lines.push("🎯 Mục tiêu 587k: " + targetProgress + "% (thiếu " + formatMoney(Math.max(0, remaining)) + ")");
    }
  }
  
  // Cảnh báo chi tiêu cafe/phụ phí
  if (transaction.category === "Cafe") {
    var cafeTotal = getCategorySpending("Cafe");
    if (cafeTotal > ALERTS.cafeBudgetWeekly) {
      lines.push("");
      lines.push("☕ *Cảnh báo:* Tiền cafe tháng này đã " + formatMoney(cafeTotal) + "! Nên cắt giảm.");
    }
  }
  
  if (transaction.category === "Phụ phí") {
    var miscTotal = getCategorySpending("Phụ phí");
    if (miscTotal > ALERTS.miscBudgetMonthly) {
      lines.push("");
      lines.push("⚠️ *Cảnh báo:* Phụ phí tháng này đã " + formatMoney(miscTotal) + "! Vượt ngân sách.");
    }
  }
  
  // Nhắc mốc thanh toán gần nhất
  var nextPayments = getNextPayment();
  if (nextPayments.length > 0 && nextPayments[0].daysLeft <= 3) {
    lines.push("");
    lines.push("🚨 " + nextPayments[0].name + " *" + formatMoney(nextPayments[0].amount) + "* - còn " + nextPayments[0].daysLeft + " ngày!");
  }
  
  sendMessage(chatId, lines.join("\n"));
}

/**
 * Xử lý các lệnh đặc biệt
 */
function handleCommand(chatId, command) {
  var parts = command.trim().split(/\s+/);
  var cmd = parts[0].toLowerCase();
  var args = parts.slice(1);
  
  switch (cmd) {
    case "/start":
    case "/help":
      sendHelp(chatId);
      break;
      
    case "/phantich":
    case "/review":
      // Phân tích tháng hiện tại hoặc tháng tùy chọn (VD: /phantich 01-2026)
      var monthArg = args.length > 0 ? args[0] : null;
      generateMonthlyAnalysis(chatId, monthArg);
      break;
      
    case "/sim":
    case "/dudoan":
      handleSimulationCommand(chatId, args);
      break;
      
    case "/von":
    case "/capital":
      handleCapitalReport(chatId);
      break;
      
    case "/setkho":
    case "/setinventory":
      handleSetInventoryCommand(chatId, args);
      break;
      
    case "/baocao":
    case "/bc":
      sendDailyReport(chatId);
      break;
      
    case "/thang":
    case "/month":
      sendMonthlyReport(chatId);
      break;
      
    case "/trend":
    case "/xuhuong":
      sendTrendReport(chatId);
      break;
      
    case "/sodu":
    case "/balance":
      sendBalanceReport(chatId);
      break;
      
    case "/no":
    case "/debt":
      sendMessage(chatId, getDebtSummary());
      break;
      
    case "/nha":
    case "/rent":
      sendRentReport(chatId);
      break;
      
    case "/mucstieu":
    case "/mt":
    case "/target":
      sendTargetReport(chatId);
      break;
      
    case "/risk":
    case "/ruiro":
      sendRiskReport(chatId);
      break;
      
    case "/tuvan":
    case "/advice":
      sendAdvice(chatId);
      break;
      
    case "/dubao":
    case "/forecast":
      sendForecastReport(chatId);
      break;
      
    case "/muctieu":
    case "/goal":
      handleGoalCommand(chatId, parts);
      break;
      
    case "/nhanvien":
    case "/nv":
      sendEmployeeReport(chatId);
      break;
      
    case "/xoa":
    case "/delete":
      handleDeleteCommand(chatId, parts);
      break;
      
    case "/bieudo":
    case "/chart":
      sendChartReport(chatId);
      break;
      
    case "/tuvan2":
    case "/phanptich":
      sendMessage(chatId, "🤖 Đang phân tích sâu toàn bộ dữ liệu...");
      var analysis = getAdvancedAnalysis();
      sendMessage(chatId, "🧠 PHÂN TÍCH SÂU TÀI CHÍNH\n━━━━━━━━━━━━━━━━━━━━\n\n" + (analysis || "Không thể phân tích lúc này."));
      break;
      
    case "/tuan":
    case "/week":
      sendWeeklyReport(chatId);
      break;
      
    case "/user":
      handleUserCommand(chatId, parts);
      break;
      
    case "/dashboard":
      var scriptUrl = ScriptApp.getService().getUrl();
      if (scriptUrl) {
        sendMessage(chatId, "📱 MINI DASHBOARD\n━━━━━━━━━━━━━━━━━━━━\n\n🔗 Mở link này trên trình duyệt:\n" + scriptUrl);
      } else {
        sendMessage(chatId, "❌ Chưa deploy web app. Trong Apps Script:\n1. Deploy → New deployment\n2. Chọn Web app\n3. Execute as: Me\n4. Access: Anyone\n5. Deploy → Copy URL");
      }
      break;
      
    case "/lichnoc":
    case "/calendar":
      sendDebtCalendar(chatId);
      break;
      
    case "/haravan":
    case "/hv":
      sendHaravanReport(chatId);
      break;
      
    case "/donhang":
    case "/orders":
      sendRecentOrders(chatId, 10);
      break;
      
    case "/sync":
      handleSyncCommand(chatId);
      break;
      
    case "/sosanh":
    case "/compare":
      sendComparisonReport(chatId);
      break;
      
    case "/whatif":
      handleWhatIf(chatId, parts);
      break;
      
    case "/note":
    case "/ghichu":
      handleNoteCommand(chatId, parts);
      break;
      
    case "/rank":
    case "/thanhtich":
      sendGamificationReport(chatId);
      break;
      
    case "/export":
      sendExportLink(chatId);
      break;
      
    case "/nhac":
    case "/remind":
      handleReminderCommand(chatId, parts);
      break;
      
    case "/debug":
      sendDebugReport(chatId);
      break;
      
    default:
      sendMessage(chatId, "❓ Lệnh không hợp lệ. Gõ /help để xem danh sách lệnh.");
  }
}

// ==================== CÁC LỆNH CỤ THỂ ====================

function sendHelp(chatId) {
  var lines = [];
  lines.push("🤖 *CHATBOT QUẢN LÝ TÀI CHÍNH*");
  lines.push("━━━━━━━━━━━━━━━━━━━━");
  lines.push("");
  lines.push("📝 *NHẬP LIỆU:*");
  lines.push("Chỉ cần nhắn tự nhiên:");
  lines.push('• "Bán đơn sách 500k"');
  lines.push('• "Ăn phở 50k"');
  lines.push('• "Cafe 35k"');
  lines.push('• "Nhận share VP 2tr"');
  lines.push("");
  lines.push("📋 *LỆNH:*");
  lines.push("/bc - Báo cáo hôm nay");
  lines.push("/thang - Báo cáo tháng (so sánh tháng trước)");
  lines.push("/trend - Xu hướng chi tiêu 3-5 tháng");
  lines.push("/sodu - Số dư tài khoản");
  lines.push("/dubao - Dự báo dòng tiền cuối tháng");
  lines.push("/no - Bảng tổng hợp nợ");
  lines.push("/nha - Tiến độ tiền nhà");
  lines.push("/nv - Lương nhân viên tháng này");
  lines.push("/mt - Mục tiêu & KPI");
  lines.push("/risk - Kiểm tra rủi ro dòng tiền");
  lines.push("/tuvan - Xin lời khuyên AI");
  lines.push("/bieudo - Biểu đồ chi tiêu");
  lines.push("");
  lines.push("⚡ *NÂNG CAO:*");
  lines.push("/muctieu Cafe 1.5tr - Đặt mục tiêu");
  lines.push("/xoa Cafe 45k - Xoá giao dịch sai");
  lines.push("/tuvan2 - Phân tích sâu AI");
  lines.push("/tuan - Báo cáo tuần");
  lines.push("/user - Quản lý multi-user");
  lines.push("/dashboard - Web dashboard");
  lines.push("");
  lines.push("🎮 *LEVEL 4:*");
  lines.push("/lichnoc - Lịch trả nợ 30 ngày");
  lines.push("/sosanh - So sánh tuần");
  lines.push("/whatif [kịch bản] - Mô phỏng AI");
  lines.push("/note [ghi chú] - Lưu ghi chú");
  lines.push("/rank - Thành tích");
  lines.push("/export - Xuất Sheet");
  lines.push("/nhac [ngày] [nd] - Nhắc nhở");
  lines.push("");
  lines.push("📦 *HARAVAN:*");
  lines.push("/haravan - Báo cáo Haravan + sync");
  lines.push("/donhang - 10 đơn gần nhất");
  lines.push("/sync - Sync doanh thu thủ công");
  lines.push("");
  lines.push("/help - Danh sách lệnh");
  lines.push("");
  lines.push("📷 Gửi *ảnh hoá đơn* → Bot tự nhận diện & ghi!");
  lines.push("💡 Hoặc hỏi bất kỳ câu gì, AI sẽ trả lời!");
  
  sendMessage(chatId, lines.join("\n"));
}

function sendDailyReport(chatId) {
  var daily = getDailySummary();
  var dailyProfit = daily.totalIncome * BUSINESS.profitMargin;
  var now = new Date();
  
  var lines = [];
  lines.push("📊 *BÁO CÁO NGÀY " + Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "dd/MM/yyyy") + "*");
  lines.push("━━━━━━━━━━━━━━━━━━━━");
  
  if (daily.count === 0) {
    lines.push("");
    lines.push("📝 Chưa có giao dịch nào hôm nay.");
    lines.push("Hãy bắt đầu nhập: 'Bán đơn sách 500k'");
  } else {
    lines.push("");
    lines.push("💰 Thu: +" + formatMoneyFull(daily.totalIncome));
    lines.push("💸 Chi tiêu: -" + formatMoneyFull(daily.totalExpense));
    
    if (daily.totalBusinessExpense > 0) {
       lines.push("📦 Nhập hàng: -" + formatMoneyFull(daily.totalBusinessExpense));
    }
    
    // Inventory Value
    var props = PropertiesService.getScriptProperties();
    var currentInventory = parseFloat(props.getProperty("INVENTORY_VALUE") || "0");
    lines.push("🏭 Tồn kho: " + formatMoneyFull(currentInventory));
    
    lines.push("📈 Ròng (Tiền mặt): " + formatMoneyFull(daily.netCash));
    lines.push("📊 Lợi nhuận (60%): " + formatMoneyFull(dailyProfit));
    
    lines.push("");
    var targetHit = dailyProfit >= BUSINESS.targetDailyAccumulation;
    lines.push("🎯 Mục tiêu 587k: " + (targetHit ? "✅ ĐẠT!" : "❌ Thiếu " + formatMoney(BUSINESS.targetDailyAccumulation - dailyProfit)));
    
    // Chi tiết giao dịch
    lines.push("");
    lines.push("📋 *Chi tiết:*");
    daily.transactions.forEach(function(tx) {
      var icon = tx.type === "Thu" ? "🟢" : "🔴";
      lines.push(icon + " " + tx.time + " " + tx.content + " " + formatMoney(tx.amount));
    });
  }
  
  // Mốc thanh toán sắp tới
  var nextPayments = getNextPayment();
  var urgent = nextPayments.filter(function(p) { return p.daysLeft <= 7; });
  if (urgent.length > 0) {
    lines.push("");
    lines.push("⚠️ *SẮP ĐẾN HẠN:*");
    urgent.forEach(function(p) {
      lines.push("• " + p.name + ": " + formatMoney(p.amount) + " (còn " + p.daysLeft + " ngày)");
    });
  }
  
  sendMessage(chatId, lines.join("\n"));
}

function sendMonthlyReport(chatId) {
  var monthly = getMonthlySummary();
  var prevMonthly = getPreviousMonthSummary();
  var now = new Date();
  var monthName = "Tháng " + Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "M/yyyy");
  
  var monthlyProfit = monthly.totalIncome * BUSINESS.profitMargin;
  var targetMonthlyRevenue = BUSINESS.targetDailyRevenue * 30;
  var revenueProgress = monthly.totalIncome > 0 ? Math.round((monthly.totalIncome / targetMonthlyRevenue) * 100) : 0;
  
  var monthStr = Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "M");
  var yearStr = Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "yyyy");
  var daysInMonth = new Date(parseInt(yearStr), parseInt(monthStr), 0).getDate();
  
  var lines = [];
  lines.push("📅 BÁO CÁO " + monthName);
  lines.push("━━━━━━━━━━━━━━━━━━━━");
  lines.push("");
  lines.push("💰 Tổng doanh thu: " + formatMoneyFull(monthly.totalIncome));
  lines.push("💸 Tổng chi: " + formatMoneyFull(monthly.totalExpense));
  lines.push("📈 Ròng: " + formatMoneyFull(monthly.netCash));
  lines.push("📊 Lợi nhuận (60%): " + formatMoneyFull(monthlyProfit));
  lines.push("");
  lines.push("📈 TB doanh thu/ngày: " + formatMoney(monthly.avgDailyIncome));
  lines.push("📆 Ngày " + monthly.daysWithData + "/" + daysInMonth);
  lines.push("🎯 Tiến độ DT tháng: " + revenueProgress + "%");
  
  // So sánh với tháng trước
  if (prevMonthly) {
    lines.push("");
    lines.push("📊 SO SÁNH VỚI THÁNG TRƯỚC (" + prevMonthly.tabName + ")");
    lines.push("━━━━━━━━━━━━━━━━━━━━");
    
    var incDiff = monthly.totalIncome - prevMonthly.totalIncome;
    var expDiff = monthly.totalExpense - prevMonthly.totalExpense;
    lines.push("💰 Thu: " + (incDiff >= 0 ? "+" : "") + formatMoney(incDiff) + " (" + (prevMonthly.totalIncome > 0 ? (incDiff >= 0 ? "+" : "") + Math.round(incDiff/prevMonthly.totalIncome*100) + "%" : "N/A") + ")");
    lines.push("💸 Chi: " + (expDiff >= 0 ? "+" : "") + formatMoney(expDiff) + " (" + (prevMonthly.totalExpense > 0 ? (expDiff >= 0 ? "+" : "") + Math.round(expDiff/prevMonthly.totalExpense*100) + "%" : "N/A") + ")");
    
    // So sánh từng danh mục chi
    var allCats = {};
    if (monthly.categoryBreakdown) Object.keys(monthly.categoryBreakdown).forEach(function(c){allCats[c]=true;});
    if (prevMonthly.categoryBreakdown) Object.keys(prevMonthly.categoryBreakdown).forEach(function(c){allCats[c]=true;});
    
    var catDiffs = [];
    Object.keys(allCats).forEach(function(cat) {
      var cur = (monthly.categoryBreakdown || {})[cat] || 0;
      var prev = (prevMonthly.categoryBreakdown || {})[cat] || 0;
      if (cur > 0 || prev > 0) {
        var diff = cur - prev;
        catDiffs.push({cat: cat, cur: cur, prev: prev, diff: diff});
      }
    });
    catDiffs.sort(function(a,b){return Math.abs(b.diff) - Math.abs(a.diff);});
    
    if (catDiffs.length > 0) {
      lines.push("");
      catDiffs.forEach(function(c) {
        var arrow = c.diff > 0 ? "📈" : (c.diff < 0 ? "📉" : "➡️");
        lines.push(arrow + " " + c.cat + ": " + formatMoney(c.cur) + " (" + (c.diff >= 0 ? "+" : "") + formatMoney(c.diff) + ")");
      });
    }
  }
  
  // Chi tiết theo danh mục (tháng hiện tại)
  if (!prevMonthly && monthly.categoryBreakdown && Object.keys(monthly.categoryBreakdown).length > 0) {
    lines.push("");
    lines.push("🏷 Theo danh mục:");
    var categories = Object.keys(monthly.categoryBreakdown);
    categories.sort(function(a, b) {
      return monthly.categoryBreakdown[b] - monthly.categoryBreakdown[a];
    });
    categories.forEach(function(cat) {
      lines.push("• " + cat + ": " + formatMoney(monthly.categoryBreakdown[cat]));
    });
  }
  
  sendMessage(chatId, lines.join("\n"));
}

/**
 * Gửi báo cáo xu hướng 3-5 tháng
 */
function sendTrendReport(chatId) {
  var months = getMultiMonthTrend();
  
  if (months.length === 0) {
    sendMessage(chatId, "❌ Không có dữ liệu tháng nào để phân tích.");
    return;
  }
  
  var lines = [];
  lines.push("📈 XU HƯỚNG CHI TIÊU (" + months.length + " tháng)");
  lines.push("━━━━━━━━━━━━━━━━━━━━");
  
  // Tổng quan từng tháng
  months.forEach(function(m) {
    var netIcon = m.net >= 0 ? "🟢" : "🔴";
    lines.push("");
    lines.push(netIcon + " " + m.tab + ": Thu " + formatMoney(m.income) + " | Chi " + formatMoney(m.expense) + " | Ròng " + (m.net >= 0 ? "+" : "") + formatMoney(m.net));
  });
  
  // Phân tích xu hướng từng danh mục chính
  if (months.length >= 2) {
    var trackedCats = ["Ăn uống", "Cafe", "Phụ phí", "Ads", "Tiền nhà", "Bán hàng"];
    lines.push("");
    lines.push("🔍 CHI TIẾT THEO DANH MỤC");
    lines.push("━━━━━━━━━━━━━━━━━━━━");
    
    trackedCats.forEach(function(cat) {
      var values = months.map(function(m) { return m.categories[cat] || 0; });
      var hasData = values.some(function(v) { return v > 0; });
      if (!hasData) return;
      
      // Xu hướng: so sánh tháng gần nhất với trung bình
      var avg = values.reduce(function(s,v){return s+v;}, 0) / values.length;
      var current = values[0];
      var trendIcon = current > avg * 1.1 ? "⬆️" : (current < avg * 0.9 ? "⬇️" : "➡️");
      
      var valuesStr = values.map(function(v) { return formatMoney(v); }).join(" → ");
      lines.push(trendIcon + " " + cat + ": " + valuesStr);
    });
  }
  
  // TB thu nhập
  if (months.length >= 2) {
    var avgIncome = months.reduce(function(s,m){return s+m.income;}, 0) / months.length;
    var avgExpense = months.reduce(function(s,m){return s+m.expense;}, 0) / months.length;
    lines.push("");
    lines.push("💡 TB thu/tháng: " + formatMoney(avgIncome));
    lines.push("💡 TB chi/tháng: " + formatMoney(avgExpense));
  }
  
  sendMessage(chatId, lines.join("\n"));
}

/**
 * Gửi báo cáo số dư tài khoản
 */
function sendBalanceReport(chatId) {
  var balanceData = getAccountBalances();
  
  if (!balanceData || balanceData.balances.length === 0) {
    sendMessage(chatId, "❌ Không đọc được số dư. Kiểm tra tab CASH FLOW trong Sheet.");
    return;
  }
  
  var lines = [];
  lines.push("🏦 SỐ DƯ TÀI KHOẢN");
  lines.push("━━━━━━━━━━━━━━━━━━━━");
  lines.push("");
  
  balanceData.balances.forEach(function(b) {
    var icon = b.amount > 0 ? "💳" : "⬜";
    if (b.amount > 1000000) icon = "💰";
    lines.push(icon + " " + b.name + ": " + formatMoneyFull(b.amount));
  });
  
  lines.push("");
  lines.push("━━━━━━━━━━━━━━━━━━━━");
  lines.push("💎 Tổng: " + formatMoneyFull(balanceData.total));
  
  // So sánh với nợ
  var totalDebt = DEBTS.reduce(function(s,d){return s+d.balance;}, 0);
  lines.push("");
  lines.push("📊 Tổng nợ: " + formatMoney(totalDebt));
  lines.push("📉 Ròng (tài sản - nợ): " + formatMoney(balanceData.total - totalDebt));
  
  sendMessage(chatId, lines.join("\n"));
}

function sendRentReport(chatId) {
  var rentProgress = getRentProgress();
  
  var lines = [];
  lines.push("🏠 *TIẾN ĐỘ TIỀN NHÀ*");
  lines.push("━━━━━━━━━━━━━━━━━━━━");
  lines.push("");
  lines.push("📅 Mốc tiếp theo: " + rentProgress.nextRentDate);
  lines.push("⏰ Còn lại: " + rentProgress.daysLeft + " ngày");
  lines.push("💰 Cần có: " + formatMoneyFull(rentProgress.amountNeeded));
  lines.push("📊 Cần tích lũy: " + formatMoney(rentProgress.dailySavingNeeded) + "/ngày");
  
  sendMessage(chatId, lines.join("\n"));
}

function sendTargetReport(chatId) {
  var daily = getDailySummary();
  var dailyProfit = daily.totalIncome * BUSINESS.profitMargin;
  var firstOfMonth = getFirstOfMonthTarget();
  var now = new Date();
  var today = now.getDate();
  
  // Tính tiền mặt cần có lũy kế đến hôm nay
  var cumulative = calculateCumulativeCashNeeded(today);
  
  var lines = [];
  lines.push("🎯 *MỤC TIÊU & KPI*");
  lines.push("━━━━━━━━━━━━━━━━━━━━");
  lines.push("");
  lines.push("*Mục tiêu hàng ngày:*");
  lines.push("• Doanh thu: " + formatMoney(BUSINESS.targetDailyRevenue) + " (~1tr/ngày)");
  lines.push("• Tích lũy: " + formatMoney(BUSINESS.targetDailyAccumulation));
  lines.push("• Hôm nay đạt: " + formatMoney(dailyProfit) + " (" + Math.round(dailyProfit / BUSINESS.targetDailyAccumulation * 100) + "%)");
  
  lines.push("");
  lines.push("*Tiền mặt cần có (lũy kế đến ngày " + today + "):*");
  lines.push("• Tổng: " + formatMoneyFull(cumulative.totalCashNeeded));
  lines.push("  - Nợ đã trả: " + formatMoney(cumulative.debtPayments.reduce(function(s,p){return s+p.amount;}, 0)));
  lines.push("  - Tích lũy nhà: " + formatMoney(cumulative.rentAccumulation));
  lines.push("  - Sinh hoạt: " + formatMoney(cumulative.livingCost));
  
  lines.push("");
  lines.push("*Đầu tháng cần có sẵn:*");
  lines.push("• " + formatMoneyFull(firstOfMonth.total));
  Object.keys(firstOfMonth.breakdown).forEach(function(key) {
    lines.push("  - " + key + ": " + formatMoney(firstOfMonth.breakdown[key]));
  });
  
  sendMessage(chatId, lines.join("\n"));
}

function sendRiskReport(chatId) {
  var risk = checkCashFlowRisk();
  
  var lines = [];
  lines.push("⚡ *KIỂM TRA RỦI RO DÒNG TIỀN*");
  lines.push("━━━━━━━━━━━━━━━━━━━━");
  lines.push("");
  lines.push("📊 Trạng thái: " + risk.riskLevel);
  lines.push("");
  lines.push("📈 Lợi nhuận dự kiến tháng: " + formatMoney(risk.projectedProfit));
  lines.push("📉 Chi phí cố định tháng: " + formatMoney(risk.totalFixedCost));
  lines.push("💰 Chênh lệch: " + (risk.gap >= 0 ? "+" : "") + formatMoney(risk.gap));
  lines.push("");
  lines.push("📊 TB doanh thu/ngày: " + formatMoney(risk.avgDailyRevenue));
  lines.push("🎯 Cần tối thiểu: " + formatMoney(BUSINESS.targetDailyRevenue) + "/ngày");
  lines.push("");
  lines.push("💡 " + risk.message);
  
  sendMessage(chatId, lines.join("\n"));
}

function sendAdvice(chatId) {
  var daily = getDailySummary();
  var monthly = getMonthlySummary();
  var risk = checkCashFlowRisk();
  var rentInfo = getRentProgress();
  
  var context = {
    todayIncome: daily.totalIncome,
    todayExpense: daily.totalExpense,
    monthIncome: monthly.totalIncome,
    monthExpense: monthly.totalExpense,
    avgDailyRevenue: monthly.avgDailyIncome,
    riskLevel: risk.riskLevel,
    cashGap: risk.gap,
    rentDaysLeft: rentInfo.daysLeft,
    rentAmount: RENT.amount,
    totalDebt: DEBTS.reduce(function(s,d){return s+d.balance;}, 0),
    totalMonthlyInterest: DEBTS.reduce(function(s,d){return s+Math.round(d.balance*d.monthlyRate);}, 0)
  };
  
  sendMessage(chatId, "🤔 Đang phân tích...");
  
  var advice = getFinancialAdvice(context);
  sendMessage(chatId, "💡 LỜI KHUYÊN TÀI CHÍNH\n━━━━━━━━━━━━━━━━━━━━\n\n" + advice);
}

// ==================== LEVEL 2 COMMAND HANDLERS ====================

/**
 * /dubao - Dự báo dòng tiền cuối tháng
 */
function sendForecastReport(chatId) {
  var forecast = getCashFlowForecast();
  if (!forecast) {
    sendMessage(chatId, "❌ Không thể dự báo. Kiểm tra dữ liệu Sheet.");
    return;
  }
  
  var now = new Date();
  var monthName = "Tháng " + Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "M");
  
  var lines = [];
  lines.push("🔮 DỰ BÁO DÒNG TIỀN " + monthName);
  lines.push("━━━━━━━━━━━━━━━━━━━━");
  lines.push("");
  lines.push("📅 Ngày " + forecast.today + "/" + forecast.daysInMonth + " (còn " + forecast.daysLeft + " ngày)");
  lines.push("");
  
  lines.push("📊 HIỆN TẠI:");
  lines.push("• Thu: " + formatMoney(forecast.currentIncome));
  lines.push("• Chi: " + formatMoney(forecast.currentExpense));
  lines.push("• TB thu/ngày: " + formatMoney(forecast.avgDailyIncome));
  lines.push("• TB chi/ngày: " + formatMoney(forecast.avgDailyExpense));
  lines.push("");
  
  lines.push("🔮 DỰ BÁO CUỐI THÁNG:");
  lines.push("• Thu dự kiến: " + formatMoney(forecast.projectedIncome));
  lines.push("• Chi dự kiến: " + formatMoney(forecast.projectedExpense));
  lines.push("• Ròng dự kiến: " + (forecast.projectedNet >= 0 ? "+" : "") + formatMoney(forecast.projectedNet));
  lines.push("");
  
  if (forecast.fixedCostsRemaining > 0) {
    lines.push("💳 Nợ cố định còn phải trả: " + formatMoney(forecast.fixedCostsRemaining));
  }
  
  if (forecast.currentBalance > 0) {
    lines.push("🏦 Số dư hiện tại: " + formatMoney(forecast.currentBalance));
    var icon = forecast.projectedEndBalance >= 0 ? "🟢" : "🔴";
    lines.push(icon + " Dư cuối tháng dự kiến: " + formatMoney(forecast.projectedEndBalance));
  }
  
  if (forecast.prevMonthIncome > 0) {
    var arrow = forecast.incomeVsPrev >= 0 ? "📈" : "📉";
    lines.push("");
    lines.push(arrow + " So với tháng trước: " + (forecast.incomeVsPrev >= 0 ? "+" : "") + formatMoney(forecast.incomeVsPrev));
  }
  
  // Lời khuyên
  lines.push("");
  if (forecast.projectedNet < 0) {
    lines.push("⚠️ CẢNH BÁO: Chi vượt thu! Cần tăng doanh thu thêm " + formatMoney(Math.abs(forecast.projectedNet)) + " trong " + forecast.daysLeft + " ngày.");
  } else if (forecast.projectedNet < 5000000) {
    lines.push("🟡 Ròng dương nhưng sát nút. Tiếp tục đẩy doanh thu!");
  } else {
    lines.push("🟢 Dự báo tích cực! Giữ vững tốc độ.");
  }
  
  sendMessage(chatId, lines.join("\n"));
}

/**
 * /muctieu - Đặt hoặc xem mục tiêu
 * Format: /muctieu → xem tất cả
 * Format: /muctieu Cafe 1500000 → đặt mục tiêu cafe max 1.5tr/tháng
 * Format: /muctieu xoa Cafe → xoá mục tiêu cafe
 */
function handleGoalCommand(chatId, parts) {
  // /muctieu → xem tiến độ
  if (parts.length <= 1) {
    sendGoalReport(chatId);
    return;
  }
  
  // /muctieu xoa [category]
  if (parts[1].toLowerCase() === "xoa" && parts.length >= 3) {
    var catToRemove = parts[2];
    removeGoal(catToRemove);
    sendMessage(chatId, "✅ Đã xoá mục tiêu: " + catToRemove);
    return;
  }
  
  // /muctieu [category] [amount]
  if (parts.length >= 3) {
    var category = parts[1];
    var amountStr = parts[2];
    
    // Parse amount
    var amount = 0;
    if (amountStr.toLowerCase().indexOf("tr") >= 0) {
      amount = parseFloat(amountStr) * 1000000;
    } else if (amountStr.toLowerCase().indexOf("k") >= 0) {
      amount = parseFloat(amountStr) * 1000;
    } else {
      amount = parseInt(amountStr);
    }
    
    if (isNaN(amount) || amount <= 0) {
      sendMessage(chatId, "❌ Số tiền không hợp lệ. VD: /muctieu Cafe 1500000 hoặc /muctieu Cafe 1.5tr");
      return;
    }
    
    // Capitalize first letter
    category = category.charAt(0).toUpperCase() + category.slice(1).toLowerCase();
    
    setGoal(category, amount, category);
    sendMessage(chatId, "✅ Đã đặt mục tiêu: " + category + " tối đa " + formatMoneyFull(amount) + "/tháng");
    return;
  }
  
  sendMessage(chatId, "📝 Cách dùng:\n/muctieu → Xem tất cả mục tiêu\n/muctieu Cafe 1500000 → Đặt mục tiêu\n/muctieu xoa Cafe → Xoá mục tiêu");
}

function sendGoalReport(chatId) {
  var results = checkGoalProgress();
  
  if (results.length === 0) {
    sendMessage(chatId, "📝 Chưa có mục tiêu nào.\n\nĐặt mục tiêu: /muctieu Cafe 1500000\n(Giới hạn cafe tối đa 1.5tr/tháng)");
    return;
  }
  
  var now = new Date();
  var today = now.getDate();
  var daysInMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate();
  
  var lines = [];
  lines.push("🎯 TIẾN ĐỘ MỤC TIÊU (ngày " + today + "/" + daysInMonth + ")");
  lines.push("━━━━━━━━━━━━━━━━━━━━");
  
  results.forEach(function(r) {
    lines.push("");
    lines.push(r.status + " " + r.label);
    
    // Progress bar
    var filled = Math.min(10, Math.round(r.percent / 10));
    var bar = "";
    for (var i = 0; i < 10; i++) {
      bar += i < filled ? "▓" : "░";
    }
    lines.push("  " + bar + " " + r.percent + "%");
    lines.push("  " + formatMoney(r.spent) + " / " + formatMoney(r.limit));
    
    if (r.remaining > 0) {
      var dailyRemaining = Math.round(r.remaining / Math.max(1, daysInMonth - today));
      lines.push("  Còn lại: " + formatMoney(r.remaining) + " (~" + formatMoney(dailyRemaining) + "/ngày)");
    } else {
      lines.push("  ❌ ĐÃ VƯỢT MỤC TIÊU!");
    }
  });
  
  sendMessage(chatId, lines.join("\n"));
}

/**
 * /nv - Báo cáo lương nhân viên
 */
function sendEmployeeReport(chatId) {
  var salaryData = getEmployeeSalaries();
  
  if (!salaryData || salaryData.employees.length === 0) {
    sendMessage(chatId, "❌ Không tìm thấy dữ liệu lương nhân viên tháng này.");
    return;
  }
  
  var now = new Date();
  var monthName = "Tháng " + (now.getMonth() + 1) + "/" + now.getFullYear();
  
  var lines = [];
  lines.push("👥 LƯƠNG NHÂN VIÊN " + monthName);
  lines.push("━━━━━━━━━━━━━━━━━━━━");
  
  salaryData.employees.forEach(function(emp) {
    lines.push("");
    lines.push("👤 " + emp.name + ": " + formatMoneyFull(emp.total));
    
    if (emp.payments.length > 0) {
      var payDetails = emp.payments.map(function(p) {
        return "ngày " + p.day + ": " + formatMoney(p.amount);
      }).join(", ");
      lines.push("  📅 " + payDetails);
    }
  });
  
  lines.push("");
  lines.push("━━━━━━━━━━━━━━━━━━━━");
  lines.push("💰 Tổng lương: " + formatMoneyFull(salaryData.total));
  
  // So sánh với tổng chi
  var monthly = getMonthlySummary();
  if (monthly.totalExpense > 0) {
    var salaryPercent = Math.round(salaryData.total / monthly.totalExpense * 100);
    lines.push("📊 Chiếm " + salaryPercent + "% tổng chi tiêu");
  }
  
  sendMessage(chatId, lines.join("\n"));
}

/**
 * /xoa - Xoá giao dịch sai
 * Format: /xoa Cafe 45000
 */
function handleDeleteCommand(chatId, parts) {
  if (parts.length < 3) {
    sendMessage(chatId, "📝 Cách dùng: /xoa [danh mục] [số tiền]\n\nVD: /xoa Cafe 45000\nVD: /xoa Ăn_uống 50k\n\nDanh mục: Cafe, Ăn_uống, Phụ_phí, Ads, Bán_hàng...");
    return;
  }
  
  var category = parts[1].replace(/_/g, " ");
  category = category.charAt(0).toUpperCase() + category.slice(1).toLowerCase();
  
  var amountStr = parts[2];
  var amount = 0;
  if (amountStr.toLowerCase().indexOf("tr") >= 0) {
    amount = parseFloat(amountStr) * 1000000;
  } else if (amountStr.toLowerCase().indexOf("k") >= 0) {
    amount = parseFloat(amountStr) * 1000;
  } else {
    amount = parseInt(amountStr);
  }
  
  if (isNaN(amount) || amount <= 0) {
    sendMessage(chatId, "❌ Số tiền không hợp lệ.");
    return;
  }
  
  var result = undoTransaction(category, amount);
  
  if (result.success) {
    sendMessage(chatId, "✅ " + result.message);
  } else {
    sendMessage(chatId, "❌ " + result.message);
  }
}

/**
 * /bieudo - Gửi biểu đồ chi tiêu
 */
function sendChartReport(chatId) {
  var monthly = getMonthlySummary();
  var cats = monthly.categoryBreakdown;
  
  if (!cats || Object.keys(cats).length === 0) {
    sendMessage(chatId, "❌ Chưa có dữ liệu chi tiêu để vẽ biểu đồ.");
    return;
  }
  
  // Tạo biểu đồ text-based (vì Google Charts API cũ đã deprecated)
  var now = new Date();
  var lines = [];
  lines.push("📊 BIỂU ĐỒ CHI TIÊU Tháng " + Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "M"));
  lines.push("━━━━━━━━━━━━━━━━━━━━");
  lines.push("");
  
  // Sort by value
  var sortedCats = Object.keys(cats).sort(function(a, b) { return cats[b] - cats[a]; });
  var maxVal = cats[sortedCats[0]] || 1;
  
  sortedCats.forEach(function(cat) {
    var val = cats[cat];
    if (val <= 0) return;
    
    var barLen = Math.max(1, Math.round(val / maxVal * 15));
    var bar = "";
    for (var i = 0; i < barLen; i++) bar += "█";
    
    var percent = monthly.totalExpense > 0 ? Math.round(val / (monthly.totalIncome + monthly.totalExpense) * 100) : 0;
    lines.push(cat);
    lines.push("  " + bar + " " + formatMoney(val) + " (" + percent + "%)");
  });
  
  lines.push("");
  lines.push("━━━━━━━━━━━━━━━━━━━━");
  
  // Thu vs Chi bar
  var totalBar = 20;
  var incomeRatio = (monthly.totalIncome + monthly.totalExpense) > 0 ? 
    Math.round(monthly.totalIncome / (monthly.totalIncome + monthly.totalExpense) * totalBar) : 0;
  var incBar = "";
  for (var j = 0; j < totalBar; j++) {
    incBar += j < incomeRatio ? "🟢" : "🔴";
  }
  lines.push("Thu vs Chi:");
  lines.push(incBar);
  lines.push("🟢 Thu " + formatMoney(monthly.totalIncome) + " | 🔴 Chi " + formatMoney(monthly.totalExpense));
  
  sendMessage(chatId, lines.join("\n"));
}


// ==================== HARAVAN INTEGRATION ====================

function haravanFetch(endpoint, params) {
  var url = HARAVAN_API_BASE + endpoint;
  if (params) {
    var q = [];
    Object.keys(params).forEach(function(k) { q.push(encodeURIComponent(k) + "=" + encodeURIComponent(params[k])); });
    if (q.length > 0) url += "?" + q.join("&");
  }
  var resp = UrlFetchApp.fetch(url, {
    method: "get",
    headers: {"Authorization": "Bearer " + HARAVAN_TOKEN, "Content-Type": "application/json"},
    muteHttpExceptions: true
  });
  if (resp.getResponseCode() !== 200) {
    Logger.log("Haravan API error: " + resp.getContentText());
    return null;
  }
  return JSON.parse(resp.getContentText());
}

function getHaravanOrders(options) {
  options = options || {};
  var params = {limit: options.limit || 50, order: "created_at desc"};
  if (options.status) params.status = options.status;
  if (options.financial_status) params.financial_status = options.financial_status;
  if (options.created_at_min) params.created_at_min = options.created_at_min;
  if (options.created_at_max) params.created_at_max = options.created_at_max;
  var result = haravanFetch("/orders.json", params);
  return result ? (result.orders || []) : [];
}

function syncHaravanRevenue(targetDate) {
  if (HARAVAN_TOKEN === "DÁN_HARAVAN_TOKEN_VÀO_ĐÂY") {
    return {success: false, message: "Chưa cấu hình Haravan token!"};
  }
  try {
    var now = targetDate || new Date();
    // Use Hanoi Time explicitly for start/end of day
    var todayStr = Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "yyyy-MM-dd");
    var startOfDay = new Date(todayStr + "T00:00:00+07:00");
    var endOfDay = new Date(todayStr + "T23:59:59+07:00");
    
    // Format ISO 8601 UTC (Z) for Haravan API to avoid offset ambiguity
    var minDate = Utilities.formatDate(startOfDay, "GMT", "yyyy-MM-dd'T'HH:mm:ss'Z'");
    var maxDate = Utilities.formatDate(endOfDay, "GMT", "yyyy-MM-dd'T'HH:mm:ss'Z'");
    
    // Lấy đơn theo cấu hình sync mode
    var filterStatus = (typeof HARAVAN_SYNC_MODE !== 'undefined' && HARAVAN_SYNC_MODE === 'all') ? null : 'paid';
    var orders = getHaravanOrders({
      financial_status: filterStatus,
      created_at_min: minDate,
      created_at_max: maxDate,
      limit: 250
    });
    
    if (orders.length === 0) {
      return { success: true, message: "Không có đơn mới (" + (filterStatus||"tất cả") + ") hôm nay.", orders: 0, revenue: 0 };
    }
    
    // Tính tổng doanh thu
    var totalRevenue = 0;
    var orderCount = 0;
    var syncedIds = [];
    
    // Lấy danh sách đơn đã sync (để tránh trùng)
    var props = PropertiesService.getScriptProperties();
    var todayStr = Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "yyyy-MM-dd");
    var syncedKey = "haravan_synced_" + todayStr;
    var syncedJson = props.getProperty(syncedKey) || "[]";
    var alreadySynced = JSON.parse(syncedJson);
    
    orders.forEach(function(order) {
      // Bỏ qua đơn huỷ
      if (order.cancelled_at) return;
      
      var orderId = String(order.id);
      if (alreadySynced.indexOf(orderId) !== -1) return; // Đã sync rồi
      
      var amount = Number(order.total_price) || 0;
      if (amount <= 0) return;
      
      totalRevenue += amount;
      orderCount++;
      syncedIds.push(orderId);
    });
    
    if (orderCount === 0) return {success: true, message: "Tất cả đơn đã được sync.", orders: 0, revenue: 0};
    
    logTransaction("Haravan (" + orderCount + " đơn)", totalRevenue, "Thu", HARAVAN_REVENUE_CATEGORY);
    
    var allSynced = alreadySynced.concat(syncedIds);
    props.setProperty(syncedKey, JSON.stringify(allSynced));
    
    var statsKey = "haravan_stats_" + todayStr;
    var prevStats = JSON.parse(props.getProperty(statsKey) || '{"orders":0,"revenue":0}');
    prevStats.orders += orderCount;
    prevStats.revenue += totalRevenue;
    props.setProperty(statsKey, JSON.stringify(prevStats));
    
    return {success: true, message: "Đã sync " + orderCount + " đơn, doanh thu: " + formatMoneyFull(totalRevenue), orders: orderCount, revenue: totalRevenue, totalOrders: prevStats.orders, totalRevenue: prevStats.revenue};
  } catch (e) {
    return {success: false, message: "Lỗi: " + e.toString()};
  }
}

function getHaravanStats() {
  var now = new Date();
  var todayStr = Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "yyyy-MM-dd");
  var startOfDay = new Date(todayStr + "T00:00:00+07:00");
  var endOfDay = new Date(todayStr + "T23:59:59+07:00");
  var minDate = Utilities.formatDate(startOfDay, "GMT", "yyyy-MM-dd'T'HH:mm:ss'Z'");
  var maxDate = Utilities.formatDate(endOfDay, "GMT", "yyyy-MM-dd'T'HH:mm:ss'Z'");
  
  var todayOrders = getHaravanOrders({created_at_min: minDate, created_at_max: maxDate, limit: 250});
  var stats = {todayTotal: todayOrders.length, todayPaid: 0, todayPending: 0, todayCancelled: 0, todayRevenue: 0, todayPendingRevenue: 0, recentOrders: todayOrders.slice(0, 5)};
  
  todayOrders.forEach(function(order) {
    var amount = Number(order.total_price) || 0;
    if (order.financial_status === "paid") { stats.todayPaid++; stats.todayRevenue += amount; }
    else if (order.cancelled_at || order.financial_status === "refunded") { stats.todayCancelled++; }
    else { stats.todayPending++; stats.todayPendingRevenue += amount; }
  });
  return stats;
}

function sendHaravanReport(chatId) {
  if (HARAVAN_TOKEN === "DÁN_HARAVAN_TOKEN_VÀO_ĐÂY") {
    sendMessage(chatId, "❌ Chưa cấu hình Haravan!\n\nTrong AllInOne.gs, tìm dòng:\nconst HARAVAN_TOKEN = \"DÁN_HARAVAN_TOKEN_VÀO_ĐÂY\"\n\nThay bằng token thật từ:\nAdmin Haravan → Apps → Private apps → Tạo app\n(Cần quyền com.read_orders)");
    return;
  }
  sendMessage(chatId, "📦 Đang kết nối Haravan...");
  try {
    var syncResult = syncHaravanRevenue();
    var stats = getHaravanStats();
    var lines = [];
    lines.push("📦 HARAVAN - " + HARAVAN_SHOP.toUpperCase());
    lines.push("━━━━━━━━━━━━━━━━━━━━");
    lines.push("");
    lines.push("📅 HÔM NAY:");
    lines.push("  📥 Tổng đơn: " + stats.todayTotal);
    lines.push("  ✅ Đã thanh toán: " + stats.todayPaid + " (" + formatMoney(stats.todayRevenue) + ")");
    lines.push("  ⏳ Chờ: " + stats.todayPending + " (" + formatMoney(stats.todayPendingRevenue) + ")");
    if (stats.todayCancelled > 0) lines.push("  ❌ Huỷ: " + stats.todayCancelled);
    lines.push("");
    lines.push("🔄 SYNC: " + (syncResult.success ? "✅" : "❌") + " " + syncResult.message);
    lines.push("");
    if (stats.recentOrders.length > 0) {
      lines.push("📋 ĐƠN GẦN ĐÂY:");
      stats.recentOrders.forEach(function(order) {
        var time = order.created_at ? Utilities.formatDate(new Date(order.created_at), "Asia/Ho_Chi_Minh", "HH:mm") : "";
        var statusIcon = order.financial_status === "paid" ? "✅" : "⏳";
        var name = order.customer ? ((order.customer.first_name || "") + " " + (order.customer.last_name || "")).trim() || "Khách" : "Khách";
        lines.push("  " + statusIcon + " " + time + " #" + order.order_number + " - " + name + " - " + formatMoney(Number(order.total_price) || 0));
      });
    }
    sendMessage(chatId, lines.join("\n"));
  } catch (e) {
    sendMessage(chatId, "❌ Lỗi Haravan: " + e.toString());
  }
}

function sendDebugReport(chatId) {
  if (HARAVAN_TOKEN === "DÁN_HARAVAN_TOKEN_VÀO_ĐÂY") {
    sendMessage(chatId, "❌ Chưa cấu hình Haravan token!");
    return;
  }
  
  sendMessage(chatId, "🕵️‍♂️ Đang debug dữ liệu Haravan...");
  
  try {
    var now = new Date();
    // Use Hanoi Time explicitly
    var todayStr = Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "yyyy-MM-dd");
    var startOfDay = new Date(todayStr + "T00:00:00+07:00");
    var endOfDay = new Date(todayStr + "T23:59:59+07:00");
    
    // Use GMT/Z to ensure strict filtering
    var minDate = Utilities.formatDate(startOfDay, "GMT", "yyyy-MM-dd'T'HH:mm:ss'Z'");
    var maxDate = Utilities.formatDate(endOfDay, "GMT", "yyyy-MM-dd'T'HH:mm:ss'Z'");
    
    var orders = getHaravanOrders({created_at_min: minDate, created_at_max: maxDate, limit: 50});
    
    var lines = [];
    lines.push("🕵️‍♂️ DEBUG HARAVAN (" + todayStr + ")");
    lines.push("Time Range: " + minDate + " -> " + maxDate);
    lines.push("Found Orders: " + orders.length);
    lines.push("━━━━━━━━━━━━━━━━━━━━");
    
    var totalPaid = 0;
    var totalPending = 0;
    
    orders.forEach(function(o) {
      var status = o.financial_status;
      if (o.cancelled_at) status = "cancelled";
      
      var amount = Number(o.total_price);
      if (status === "paid") totalPaid += amount;
      else if (status !== "cancelled" && status !== "refunded") totalPending += amount;
      
      var icon = status === "paid" ? "✅" : (status === "cancelled" ? "❌" : "⏳");
      lines.push(icon + " #" + o.order_number + " [" + status + "] " + formatMoney(amount));
      lines.push("   🕒 " + Utilities.formatDate(new Date(o.created_at), "Asia/Ho_Chi_Minh", "HH:mm"));
    });
    
    lines.push("━━━━━━━━━━━━━━━━━━━━");
    lines.push("✅ Paid Total: " + formatMoney(totalPaid));
    lines.push("⏳ Pending Total: " + formatMoney(totalPending));
    lines.push("💰 SUM: " + formatMoney(totalPaid + totalPending));
    
    sendMessage(chatId, lines.join("\n"));
    
  } catch (e) {
    sendMessage(chatId, "❌ Debug Error: " + e.toString());
  }
}

function sendRecentOrders(chatId, limit) {
  if (HARAVAN_TOKEN === "DÁN_HARAVAN_TOKEN_VÀO_ĐÂY") { sendMessage(chatId, "❌ Chưa cấu hình Haravan token!"); return; }
  try {
    var orders = getHaravanOrders({limit: limit || 10});
    if (orders.length === 0) { sendMessage(chatId, "📦 Không có đơn hàng nào."); return; }
    var lines = [];
    lines.push("📦 ĐƠN HÀNG GẦN ĐÂY (" + orders.length + ")");
    lines.push("━━━━━━━━━━━━━━━━━━━━");
    var totalRev = 0;
    orders.forEach(function(order) {
      var time = order.created_at ? Utilities.formatDate(new Date(order.created_at), "Asia/Ho_Chi_Minh", "dd/MM HH:mm") : "";
      var statusIcon = order.financial_status === "paid" ? "✅" : order.cancelled_at ? "❌" : "⏳";
      var name = order.customer ? ((order.customer.first_name || "") + " " + (order.customer.last_name || "")).trim() || "Khách" : "Khách";
      var amount = Number(order.total_price) || 0;
      if (order.financial_status === "paid") totalRev += amount;
      var items = "";
      if (order.line_items && order.line_items.length > 0) {
        items = order.line_items.map(function(i) { return i.title + (i.quantity > 1 ? " x" + i.quantity : ""); }).join(", ");
        if (items.length > 60) items = items.substring(0, 57) + "...";
      }
      lines.push("");
      lines.push(statusIcon + " #" + order.order_number + " | " + time);
      lines.push("   👤 " + name + " | 💰 " + formatMoney(amount));
      if (items) lines.push("   📦 " + items);
    });
    lines.push("");
    lines.push("━━━━━━━━━━━━━━━━━━━━");
    lines.push("💰 Tổng đã thu: " + formatMoneyFull(totalRev));
    sendMessage(chatId, lines.join("\n"));
  } catch (e) {
    sendMessage(chatId, "❌ Lỗi: " + e.toString());
  }
}

function handleSyncCommand(chatId) {
  sendMessage(chatId, "🔄 Đang sync doanh thu từ Haravan...");
  var result = syncHaravanRevenue();
  if (result.success) {
    var lines = ["✅ SYNC THÀNH CÔNG", "━━━━━━━━━━━━━━━━━━━━", "", result.message];
    if (result.orders > 0) lines.push("", "📅 Tổng ngày: " + result.totalOrders + " đơn, " + formatMoneyFull(result.totalRevenue));
    sendMessage(chatId, lines.join("\n"));
  } else {
    sendMessage(chatId, "❌ " + result.message);
  }
}

function setupHaravanSync() {
  var triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(function(t) { if (t.getHandlerFunction() === "autoSyncHaravan") ScriptApp.deleteTrigger(t); });
  ScriptApp.newTrigger("autoSyncHaravan").timeBased().everyHours(1).create();
  sendMessage(OWNER_CHAT_ID, "✅ Đã thiết lập auto-sync Haravan mỗi 1 giờ!");
}

function autoSyncHaravan() {
  if (HARAVAN_TOKEN === "DÁN_HARAVAN_TOKEN_VÀO_ĐÂY") return;
  var result = syncHaravanRevenue();
  if (result.success && result.orders > 0) {
    sendMessage(OWNER_CHAT_ID, "🔔 Haravan sync: " + result.message);
  }
}

// ==================== LEVEL 4 FEATURES ====================

/**
 * /lichnoc - Lịch trả nợ 30 ngày tới
 */
function sendDebtCalendar(chatId) {
  var now = new Date();
  var todayStr = Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "d");
  var today = parseInt(todayStr);
  var monthStr = Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "M");
  var month = parseInt(monthStr) - 1; // 0-indexed for calculation compatibility
  var yearStr = Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "yyyy");
  var year = parseInt(yearStr);
  var daysInMonth = new Date(year, month + 1, 0).getDate();
  
  var lines = [];
  lines.push("🗓️ LỊCH TRẢ NỢ 30 NGÀY TỚI");
  lines.push("━━━━━━━━━━━━━━━━━━━━");
  lines.push("");
  
  // Thu thập tất cả ngày trả nợ
  var payments = [];
  DEBTS.forEach(function(d) {
    if (!d.payDay || d.monthlyPayment <= 0) return;
    
    // Tháng này
    if (d.payDay >= today) {
      var daysLeft = d.payDay - today;
      payments.push({
        day: d.payDay, month: month + 1, year: year,
        name: d.fullName, amount: d.monthlyPayment,
        daysLeft: daysLeft, interest: Math.round(d.balance * d.monthlyRate)
      });
    }
    
    // Tháng sau
    var nextMonth = month + 1;
    var nextYear = year;
    if (nextMonth > 11) { nextMonth = 0; nextYear++; }
    var futureDay = d.payDay;
    var daysLeftNext = (daysInMonth - today) + futureDay;
    if (daysLeftNext <= 30 && d.payDay < today) {
      payments.push({
        day: futureDay, month: nextMonth + 1, year: nextYear,
        name: d.fullName, amount: d.monthlyPayment,
        daysLeft: daysLeftNext, interest: Math.round(d.balance * d.monthlyRate)
      });
    }
  });
  
  // Sort theo ngày
  payments.sort(function(a, b) { return a.daysLeft - b.daysLeft; });
  
  var totalUpcoming = 0;
  payments.forEach(function(p) {
    var urgency = p.daysLeft <= 3 ? "🔴" : p.daysLeft <= 7 ? "🟡" : "🟢";
    var dateStr = ("0" + p.day).slice(-2) + "/" + ("0" + p.month).slice(-2);
    
    lines.push(urgency + " " + dateStr + " — " + p.name);
    lines.push("   💰 Trả: " + formatMoney(p.amount) + " (lãi: " + formatMoney(p.interest) + ")");
    lines.push("   ⏰ Còn " + p.daysLeft + " ngày");
    lines.push("");
    totalUpcoming += p.amount;
  });
  
  if (payments.length === 0) {
    lines.push("✅ Không có khoản nợ nào đến hạn trong 30 ngày tới!");
  } else {
    lines.push("━━━━━━━━━━━━━━━━━━━━");
    lines.push("💳 Tổng cần trả: " + formatMoneyFull(totalUpcoming));
    
    // Kiểm tra đủ tiền không
    var balanceData = getAccountBalances();
    if (balanceData && balanceData.total > 0) {
      var diff = balanceData.total - totalUpcoming;
      if (diff >= 0) {
        lines.push("🟢 Đủ tiền trả! Dư " + formatMoney(diff));
      } else {
        lines.push("🔴 Thiếu " + formatMoney(Math.abs(diff)) + "! Cần tăng doanh thu.");
      }
    }
  }
  
  sendMessage(chatId, lines.join("\n"));
}

/**
 * /sosanh - So sánh tuần này vs tuần trước
 */
function sendComparisonReport(chatId) {
  try {
    var now = new Date();
    var today = parseInt(Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "d"));
    var sheet = getMonthSheet();
    if (!sheet) {
      sendMessage(chatId, "❌ Không tìm thấy dữ liệu tháng này.");
      return;
    }
    
    var lastRow = sheet.getLastRow();
    var lastCol = sheet.getLastColumn();
    var data = sheet.getRange(1, 1, lastRow, lastCol).getValues();
    
    // Tuần này (7 ngày gần nhất)
    var thisWeekStart = Math.max(1, today - 6);
    var lastWeekStart = Math.max(1, today - 13);
    var lastWeekEnd = Math.max(1, today - 7);
    
    var thisWeek = {income: 0, expense: 0, cats: {}};
    var lastWeek = {income: 0, expense: 0, cats: {}};
    
    for (var i = 1; i < data.length; i++) {
      var catName = String(data[i][0]).toUpperCase().trim();
      if (catName === "TỔNG CHI" || catName === "LỢI NHUẬN" || catName === "CUỐI NGÀY" || !catName) continue;
      var catInfo = CATEGORY_MAP[catName];
      if (!catInfo) continue;
      
      // Tuần này
      for (var d = thisWeekStart; d <= today; d++) {
        var val = Number(data[i][d + 1]) || 0;
        if (val > 0) {
          if (catInfo.type === "Thu") thisWeek.income += val;
          else thisWeek.expense += val;
          thisWeek.cats[catInfo.botCategory] = (thisWeek.cats[catInfo.botCategory] || 0) + val;
        }
      }
      
      // Tuần trước
      for (var d2 = lastWeekStart; d2 <= lastWeekEnd; d2++) {
        if (d2 < 1) continue;
        var val2 = Number(data[i][d2 + 1]) || 0;
        if (val2 > 0) {
          if (catInfo.type === "Thu") lastWeek.income += val2;
          else lastWeek.expense += val2;
          lastWeek.cats[catInfo.botCategory] = (lastWeek.cats[catInfo.botCategory] || 0) + val2;
        }
      }
    }
    
    var lines = [];
    lines.push("📊 SO SÁNH TUẦN");
    lines.push("━━━━━━━━━━━━━━━━━━━━");
    lines.push("");
    
    // Thu nhập
    var incDiff = thisWeek.income - lastWeek.income;
    var incArrow = incDiff >= 0 ? "📈 +" : "📉 ";
    lines.push("💰 THU NHẬP:");
    lines.push("  Tuần này: " + formatMoney(thisWeek.income));
    lines.push("  Tuần trước: " + formatMoney(lastWeek.income));
    lines.push("  " + incArrow + formatMoney(Math.abs(incDiff)));
    lines.push("");
    
    // Chi tiêu
    var expDiff = thisWeek.expense - lastWeek.expense;
    var expArrow = expDiff <= 0 ? "📉 " : "📈 +";
    lines.push("💸 CHI TIÊU:");
    lines.push("  Tuần này: " + formatMoney(thisWeek.expense));
    lines.push("  Tuần trước: " + formatMoney(lastWeek.expense));
    lines.push("  " + expArrow + formatMoney(Math.abs(expDiff)) + (expDiff > 0 ? " ⚠️" : " ✅"));
    lines.push("");
    
    // So sánh từng category
    lines.push("📋 CHI TIẾT THAY ĐỔI:");
    var allCats = {};
    Object.keys(thisWeek.cats).forEach(function(c) { allCats[c] = true; });
    Object.keys(lastWeek.cats).forEach(function(c) { allCats[c] = true; });
    
    Object.keys(allCats).forEach(function(cat) {
      var tw = thisWeek.cats[cat] || 0;
      var lw = lastWeek.cats[cat] || 0;
      if (tw === 0 && lw === 0) return;
      var diff = tw - lw;
      var arrow = diff > 0 ? "↑" : diff < 0 ? "↓" : "=";
      lines.push("  " + arrow + " " + cat + ": " + formatMoney(tw) + " (was " + formatMoney(lw) + ")");
    });
    
    sendMessage(chatId, lines.join("\n"));
  } catch (e) {
    sendMessage(chatId, "❌ Lỗi so sánh: " + e.toString());
  }
}

/**
 * /whatif - Kịch bản "What If" dùng Gemini
 */
function handleWhatIf(chatId, parts) {
  var scenario = parts.slice(1).join(" ");
  if (!scenario) {
    sendMessage(chatId, "📝 Cách dùng:\n/whatif trả thêm 2tr cho VP Bank\n/whatif giảm cafe xuống 500k/tháng\n/whatif tăng doanh thu lên 30tr/tháng\n/whatif vay thêm 10tr lãi 2%");
    return;
  }
  
  sendMessage(chatId, "🧮 Đang tính toán kịch bản...");
  
  var debtDetails = DEBTS.map(function(d) {
    return d.fullName + ": dư nợ " + formatMoney(d.balance) + ", lãi " + (d.monthlyRate * 100) + "%/tháng, trả " + formatMoney(d.monthlyPayment) + "/tháng";
  }).join("\n");
  
  var monthly = getMonthlySummary();
  
  var systemPrompt = 'Bạn là chuyên gia phân tích tài chính. Tính toán CHÍNH XÁC kịch bản "what if".\n' +
    'Trả lời bằng tiếng Việt, dùng emoji, ngắn gọn (tối đa 300 từ).\n' +
    'Đưa ra: (1) Kết quả cụ thể bằng số (2) So sánh trước/sau (3) Đánh giá nên hay không nên làm.';
  
  var prompt = 'TÌNH HÌNH HIỆN TẠI:\n' +
    'Thu tháng: ' + formatMoney(monthly.totalIncome) + '\n' +
    'Chi tháng: ' + formatMoney(monthly.totalExpense) + '\n' +
    'Biên LN: 60%\n' +
    'Tiền nhà: ' + formatMoney(RENT.amount) + '/tháng\n\n' +
    'CÁC KHOẢN NỢ:\n' + debtDetails + '\n' +
    'Tổng nợ: ' + formatMoney(DEBTS.reduce(function(s,d){return s+d.balance;}, 0)) + '\n' +
    'Tổng lãi/tháng: ' + formatMoney(DEBTS.reduce(function(s,d){return s+Math.round(d.balance*d.monthlyRate);}, 0)) + '\n\n' +
    'KỊCH BẢN: "' + scenario + '"\n\n' +
    'Hãy phân tích cụ thể: lãi tiết kiệm được, thời gian rút ngắn, ảnh hưởng dòng tiền.';
  
  var result = callGemini(prompt, systemPrompt, GEMINI_MODEL_SMART);
  sendMessage(chatId, "🧮 KỊCH BẢN: " + scenario + "\n━━━━━━━━━━━━━━━━━━━━\n\n" + (result || "Không thể phân tích."));
}

/**
 * /note - Ghi chú nhanh
 */
function handleNoteCommand(chatId, parts) {
  var props = PropertiesService.getScriptProperties();
  
  if (parts.length <= 1) {
    // Xem tất cả notes
    var notesJson = props.getProperty("user_notes") || "[]";
    var notes = JSON.parse(notesJson);
    
    if (notes.length === 0) {
      sendMessage(chatId, "📝 Chưa có ghi chú nào.\n\nThêm ghi chú: /note Nhớ thu tiền khách A\nXoá: /note xoa 1");
      return;
    }
    
    var lines = [];
    lines.push("📌 GHI CHÚ (" + notes.length + ")");
    lines.push("━━━━━━━━━━━━━━━━━━━━");
    
    notes.forEach(function(n, idx) {
      lines.push("");
      lines.push((idx + 1) + ". " + n.text);
      lines.push("   📅 " + n.date);
    });
    
    lines.push("");
    lines.push("Xoá: /note xoa [số]");
    sendMessage(chatId, lines.join("\n"));
    return;
  }
  
  // Xoá note
  if (parts[1].toLowerCase() === "xoa" && parts[2]) {
    var idx = parseInt(parts[2]) - 1;
    var notesJson2 = props.getProperty("user_notes") || "[]";
    var notes2 = JSON.parse(notesJson2);
    
    if (idx >= 0 && idx < notes2.length) {
      var removed = notes2.splice(idx, 1);
      props.setProperty("user_notes", JSON.stringify(notes2));
      sendMessage(chatId, "✅ Đã xoá: " + removed[0].text);
    } else {
      sendMessage(chatId, "❌ Số không hợp lệ.");
    }
    return;
  }
  
  // Thêm note mới
  var noteText = parts.slice(1).join(" ");
  var notesJson3 = props.getProperty("user_notes") || "[]";
  var notes3 = JSON.parse(notesJson3);
  var now = new Date();
  
  notes3.push({
    text: noteText,
    date: Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "dd/MM HH:mm")
  });
  
  // Giới hạn 20 notes
  if (notes3.length > 20) notes3 = notes3.slice(-20);
  
  props.setProperty("user_notes", JSON.stringify(notes3));
  sendMessage(chatId, "📌 Đã lưu ghi chú #" + notes3.length + ":\n\"" + noteText + "\"");
}

/**
 * Gamification - Streak, badges, rank
 */
function getGamificationStatus() {
  var props = PropertiesService.getScriptProperties();
  var now = new Date();
  var todayStr = Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "yyyy-MM-dd");
  
  // Streak tracking (Hanoi Time)
  var lastActiveDay = props.getProperty("last_active_day") || "";
  var streak = parseInt(props.getProperty("streak_days") || "0");
  var totalDays = parseInt(props.getProperty("total_active_days") || "0");
  var totalTransactions = parseInt(props.getProperty("total_transactions") || "0");
  
  // Calculate yesterday in Hanoi Time
  var todayDateHanoi = new Date(todayStr + "T00:00:00+07:00");
  var yesterdayDateHanoi = new Date(todayDateHanoi.getTime() - 24*60*60*1000);
  var yesterdayStr = Utilities.formatDate(yesterdayDateHanoi, "Asia/Ho_Chi_Minh", "yyyy-MM-dd");
  
  if (lastActiveDay === todayStr) {
    // Đã ghi nhận hôm nay
  } else if (lastActiveDay === yesterdayStr) {
    streak++;
    totalDays++;
    props.setProperty("streak_days", String(streak));
    props.setProperty("total_active_days", String(totalDays));
    props.setProperty("last_active_day", todayStr);
  } else {
    streak = 1;
    totalDays++;
    props.setProperty("streak_days", "1");
    props.setProperty("total_active_days", String(totalDays));
    props.setProperty("last_active_day", todayStr);
  }
  
  // Badges
  var badges = [];
  if (streak >= 7) badges.push("🔥 7-Day Streak");
  if (streak >= 30) badges.push("💎 30-Day Streak");
  if (totalDays >= 30) badges.push("📅 1 Tháng Kiên Trì");
  if (totalTransactions >= 100) badges.push("💰 100 Giao Dịch");
  if (totalTransactions >= 500) badges.push("🏆 500 Giao Dịch");
  
  // Financial rank
  var monthly = getMonthlySummary();
  var savingsRate = monthly.totalIncome > 0 ? Math.round((monthly.totalIncome - monthly.totalExpense) / monthly.totalIncome * 100) : 0;
  
  var rank = "🥉 Tân Binh";
  if (savingsRate >= 30) rank = "🥈 Tiết Kiệm Giỏi";
  if (savingsRate >= 50) rank = "🥇 Quản Lý Tài Ba";
  if (savingsRate >= 70) rank = "💎 Bậc Thầy Tài Chính";
  if (savingsRate < 0) rank = "🆘 Cần Cải Thiện";
  
  // Points
  var points = (streak * 10) + (totalDays * 5) + (totalTransactions * 2);
  
  return {
    streak: streak,
    totalDays: totalDays,
    totalTransactions: totalTransactions,
    badges: badges,
    rank: rank,
    savingsRate: savingsRate,
    points: points
  };
}

function recordTransaction() {
  var props = PropertiesService.getScriptProperties();
  var count = parseInt(props.getProperty("total_transactions") || "0");
  props.setProperty("total_transactions", String(count + 1));
  
  var todayStr = Utilities.formatDate(new Date(), "Asia/Ho_Chi_Minh", "yyyy-MM-dd");
  props.setProperty("last_active_day", todayStr);
}

function sendGamificationReport(chatId) {
  var status = getGamificationStatus();
  
  var lines = [];
  lines.push("🏆 THÀNH TÍCH CỦA BẠN");
  lines.push("━━━━━━━━━━━━━━━━━━━━");
  lines.push("");
  lines.push("🎖️ Rank: " + status.rank);
  lines.push("⭐ Điểm: " + status.points);
  lines.push("");
  lines.push("🔥 Streak: " + status.streak + " ngày liên tục");
  lines.push("📅 Tổng ngày hoạt động: " + status.totalDays);
  lines.push("💰 Tổng giao dịch: " + status.totalTransactions);
  lines.push("💹 Tỷ lệ tiết kiệm: " + status.savingsRate + "%");
  lines.push("");
  
  if (status.badges.length > 0) {
    lines.push("🏅 BADGES:");
    status.badges.forEach(function(b) { lines.push("  " + b); });
  } else {
    lines.push("🏅 Chưa có badge. Ghi chép 7 ngày liên tục để nhận badge đầu tiên!");
  }
  
  // Next milestone
  lines.push("");
  if (status.streak < 7) {
    lines.push("🎯 Tiếp theo: " + (7 - status.streak) + " ngày nữa → 🔥 7-Day Streak");
  } else if (status.streak < 30) {
    lines.push("🎯 Tiếp theo: " + (30 - status.streak) + " ngày nữa → 💎 30-Day Streak");
  }
  
  sendMessage(chatId, lines.join("\n"));
}

/**
 * /export - Gửi link Google Sheet
 */
function sendExportLink(chatId) {
  var url = "https://docs.google.com/spreadsheets/d/" + SPREADSHEET_ID;
  var now = new Date();
  var monthName = "Tháng " + Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "M/yyyy");
  
  var lines = [];
  lines.push("📤 EXPORT DỮ LIỆU");
  lines.push("━━━━━━━━━━━━━━━━━━━━");
  lines.push("");
  lines.push("📊 Google Sheet (" + monthName + "):");
  lines.push(url);
  lines.push("");
  lines.push("📋 Tab hiện tại: " + getCurrentMonthTab());
  lines.push("");
  lines.push("💡 Mở link → File → Download → Excel/PDF");
  
  sendMessage(chatId, lines.join("\n"));
}

/**
 * /nhac - Nhắc nhở tuỳ chỉnh
 */
function handleReminderCommand(chatId, parts) {
  var props = PropertiesService.getScriptProperties();
  
  if (parts.length <= 1) {
    var remJson = props.getProperty("custom_reminders") || "[]";
    var reminders = JSON.parse(remJson);
    
    if (reminders.length === 0) {
      sendMessage(chatId, "⏰ Chưa có nhắc nhở nào.\n\nThêm: /nhac 25 Trả nợ TP Bank 1tr\n(Nhắc vào ngày 25 hàng tháng)");
      return;
    }
    
    var lines = [];
    lines.push("⏰ NHẮC NHỞ (" + reminders.length + ")");
    lines.push("━━━━━━━━━━━━━━━━━━━━");
    
    reminders.forEach(function(r, idx) {
      lines.push("");
      lines.push((idx + 1) + ". Ngày " + r.day + " — " + r.text);
    });
    
    lines.push("");
    lines.push("Xoá: /nhac xoa [số]");
    sendMessage(chatId, lines.join("\n"));
    return;
  }
  
  // Xoá reminder
  if (parts[1].toLowerCase() === "xoa" && parts[2]) {
    var idx = parseInt(parts[2]) - 1;
    var remJson2 = props.getProperty("custom_reminders") || "[]";
    var rems = JSON.parse(remJson2);
    if (idx >= 0 && idx < rems.length) {
      var removed = rems.splice(idx, 1);
      props.setProperty("custom_reminders", JSON.stringify(rems));
      sendMessage(chatId, "✅ Đã xoá nhắc nhở: " + removed[0].text);
    }
    return;
  }
  
  // Thêm reminder: /nhac [ngày] [nội dung]
  var day = parseInt(parts[1]);
  if (isNaN(day) || day < 1 || day > 31) {
    sendMessage(chatId, "❌ Ngày không hợp lệ. VD: /nhac 25 Trả nợ TP Bank");
    return;
  }
  
  var reminderText = parts.slice(2).join(" ");
  if (!reminderText) {
    sendMessage(chatId, "❌ Thiếu nội dung. VD: /nhac 25 Trả nợ TP Bank 1tr");
    return;
  }
  
  var remJson3 = props.getProperty("custom_reminders") || "[]";
  var rems3 = JSON.parse(remJson3);
  rems3.push({day: day, text: reminderText});
  rems3.sort(function(a, b) { return a.day - b.day; });
  props.setProperty("custom_reminders", JSON.stringify(rems3));
  
  sendMessage(chatId, "⏰ Đã đặt nhắc nhở:\nNgày " + day + " hàng tháng: " + reminderText);
}

/**
 * Kiểm tra nhắc nhở tuỳ chỉnh (gọi trong autoDailyMorning)
 */
function checkCustomReminders() {
  var props = PropertiesService.getScriptProperties();
  var remJson = props.getProperty("custom_reminders") || "[]";
  var reminders = JSON.parse(remJson);
  if (reminders.length === 0) return;
  
  var today = new Date().getDate();
  
  reminders.forEach(function(r) {
    if (r.day === today) {
      sendMessage(OWNER_CHAT_ID, "⏰ NHẮC NHỞ HÔM NAY:\n\n📌 " + r.text);
    }
    // Nhắc trước 1 ngày
    if (r.day === today + 1) {
      sendMessage(OWNER_CHAT_ID, "⏰ NHẮC NHỞ NGÀY MAI:\n\n📌 " + r.text);
    }
  });
}

// ==================== LEVEL 3 FEATURES ====================

/**
 * Nhận diện ảnh bill/hoá đơn bằng Gemini Vision
 */
function processPhoto(chatId, message) {
  try {
    sendMessage(chatId, "📷 Đang phân tích ảnh...");
    
    // Lấy ảnh có resolution cao nhất
    var photos = message.photo;
    var bestPhoto = photos[photos.length - 1];
    var fileId = bestPhoto.file_id;
    
    // Lấy URL file từ Telegram
    var fileUrl = "https://api.telegram.org/bot" + TELEGRAM_TOKEN + "/getFile?file_id=" + fileId;
    var fileResponse = UrlFetchApp.fetch(fileUrl, {muteHttpExceptions: true});
    var fileData = JSON.parse(fileResponse.getContentText());
    
    if (!fileData.ok || !fileData.result.file_path) {
      sendMessage(chatId, "❌ Không thể tải ảnh. Thử lại sau.");
      return;
    }
    
    var downloadUrl = "https://api.telegram.org/file/bot" + TELEGRAM_TOKEN + "/" + fileData.result.file_path;
    
    // Tải ảnh
    var imageResponse = UrlFetchApp.fetch(downloadUrl);
    var imageBlob = imageResponse.getBlob();
    var base64Image = Utilities.base64Encode(imageBlob.getBytes());
    var mimeType = imageBlob.getContentType() || "image/jpeg";
    
    // Gọi Gemini Vision API
    var apiUrl = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=" + GEMINI_API_KEY;
    
    var caption = message.caption || "";
    
    var payload = {
      contents: [{
        parts: [
          {
            text: 'Phân tích ảnh hoá đơn/bill này. Trích xuất thông tin:\n' +
              '- Tổng tiền (VNĐ)\n- Mô tả ngắn gọn\n- Loại chi tiêu: Ăn uống, Cafe, Xăng xe, Điện nước, Phụ phí, Nhập hàng, Khác\n\n' +
              'Ghi chú thêm từ người dùng: ' + caption + '\n\n' +
              'Trả về CHÍNH XÁC JSON (không markdown):\n' +
              '{"amount": <số_tiền>, "content": "<mô_tả>", "type": "Chi", "category": "<danh_mục>", "confidence": "<cao/trung_bình/thấp>"}\n\n' +
              'Nếu KHÔNG PHẢI hoá đơn, trả về:\n' +
              '{"amount": 0, "content": "", "type": "none", "category": "none", "confidence": "none"}'
          },
          {
            inlineData: {
              mimeType: mimeType,
              data: base64Image
            }
          }
        ]
      }],
      generationConfig: {
        temperature: 0.1,
        maxOutputTokens: 1024
      }
    };
    
    var options = {
      method: "post",
      contentType: "application/json",
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    };
    
    var response = UrlFetchApp.fetch(apiUrl, options);
    var json = JSON.parse(response.getContentText());
    
    if (!json.candidates || !json.candidates[0] || !json.candidates[0].content) {
      sendMessage(chatId, "❌ Không thể phân tích ảnh. API error.");
      return;
    }
    
    var resultText = json.candidates[0].content.parts[0].text;
    var cleaned = resultText.replace(/```json\s*/g, "").replace(/```\s*/g, "").trim();
    
    try {
      var result = JSON.parse(cleaned);
      
      if (result.type === "none" || result.amount === 0) {
        sendMessage(chatId, "🤔 Không nhận diện được hoá đơn. Thử chụp rõ hơn hoặc nhập tay!");
        return;
      }
      
      // Hiển thị kết quả và hỏi xác nhận
      var lines = [];
      lines.push("🧾 NHẬN DIỆN HOÁ ĐƠN");
      lines.push("━━━━━━━━━━━━━━━━━━━━");
      lines.push("");
      lines.push("📝 " + result.content);
      lines.push("💰 " + formatMoneyFull(result.amount));
      lines.push("📂 " + result.category);
      lines.push("🎯 Độ tin cậy: " + result.confidence);
      lines.push("");
      
      // Auto-log nếu confidence cao
      if (result.confidence === "cao" || result.confidence === "high") {
        logTransaction(result.content, result.amount, result.type, result.category);
        lines.push("✅ Đã tự động ghi vào Sheet!");
        
        var daily = getDailySummary();
        lines.push("📊 Tổng chi hôm nay: " + formatMoney(daily.totalExpense));
      } else {
        lines.push("⚠️ Độ tin cậy chưa cao.");
        lines.push("Gõ: " + result.content + " " + formatMoney(result.amount));
        lines.push("để xác nhận ghi vào Sheet.");
      }
      
      sendMessage(chatId, lines.join("\n"));
      
    } catch (parseError) {
      sendMessage(chatId, "📷 Kết quả phân tích:\n\n" + resultText);
    }
    
  } catch (error) {
    Logger.log("processPhoto error: " + error.toString());
    sendMessage(chatId, "❌ Lỗi xử lý ảnh: " + error.toString());
  }
}

/**
 * AI Advisor nâng cao - Phân tích sâu + kế hoạch trả nợ tối ưu
 */
function getAdvancedAnalysis() {
  // Thu thập data 6 tháng
  var months = getMultiMonthTrend();
  var monthly = getMonthlySummary();
  var risk = checkCashFlowRisk();
  var goals = checkGoalProgress();
  var forecast = getCashFlowForecast();
  
  var historicalData = months.map(function(m) {
    return m.tab + ": Thu " + formatMoney(m.income) + ", Chi " + formatMoney(m.expense) + ", Ròng " + formatMoney(m.income - m.expense);
  }).join("\n");
  
  var debtDetails = DEBTS.map(function(d) {
    return d.fullName + ": " + formatMoney(d.balance) + " (lãi " + (d.monthlyRate * 100) + "%/tháng, trả " + formatMoney(d.monthlyPayment) + "/tháng)";
  }).join("\n");
  
  var goalStr = goals.length > 0 ? goals.map(function(g) {
    return g.label + ": " + formatMoney(g.spent) + "/" + formatMoney(g.limit) + " (" + g.percent + "%)";
  }).join("\n") : "Chưa đặt mục tiêu";
  
  var systemPrompt = 'Bạn là chuyên gia tài chính cá nhân với 20 năm kinh nghiệm.\n' +
    'Phân tích TOÀN DIỆN tình hình tài chính và đưa ra KẾ HOẠCH CỤ THỂ.\n' +
    'Trả lời bằng tiếng Việt, dùng emoji. Tối đa 500 từ.\n\n' +
    'YÊU CẦU:\n' +
    '1. Đánh giá tổng quan (1 đoạn ngắn)\n' +
    '2. Top 3 vấn đề cần giải quyết ngay\n' +
    '3. Kế hoạch trả nợ tối ưu (thứ tự ưu tiên dựa trên lãi suất)\n' +
    '4. Mục tiêu cắt giảm cụ thể 3 tháng tới\n' +
    '5. Dự báo thời gian hết nợ nếu theo kế hoạch';
  
  var prompt = 'DỮ LIỆU TÀI CHÍNH THỰC TẾ:\n\n' +
    '📊 LỊCH SỬ THU CHI (3-6 tháng):\n' + historicalData + '\n\n' +
    '💳 CHI TIẾT NỢ:\n' + debtDetails + '\n' +
    'Tổng nợ: ' + formatMoney(DEBTS.reduce(function(s,d){return s+d.balance;}, 0)) + '\n\n' +
    '📅 THÁNG NÀY:\n' +
    'Thu: ' + formatMoney(monthly.totalIncome) + '\n' +
    'Chi: ' + formatMoney(monthly.totalExpense) + '\n' +
    'Biên lợi nhuận kinh doanh: 60%\n' +
    'Tiền nhà: ' + formatMoney(RENT.amount) + '/tháng\n\n' +
    '🎯 MỤC TIÊU HIỆN TẠI:\n' + goalStr + '\n\n' +
    '🔮 DỰ BÁO CUỐI THÁNG:\n' +
    (forecast ? 'Thu dự kiến: ' + formatMoney(forecast.projectedIncome) + ', Chi: ' + formatMoney(forecast.projectedExpense) : 'Chưa có dữ liệu') + '\n\n' +
    '⚠️ RỦI RO:\n' + (risk.riskLevel || 'N/A') + '\n\n' +
    'Hãy phân tích và đưa kế hoạch hành động cụ thể.';
  
  return callGemini(prompt, systemPrompt, GEMINI_MODEL_SMART);
}

/**
 * Báo cáo tổng kết tuần
 */
function sendWeeklyReport(chatId) {
  var targetChatId = chatId || OWNER_CHAT_ID;
  
  try {
    var now = new Date();
    var monthly = getMonthlySummary();
    var forecast = getCashFlowForecast();
    var goals = checkGoalProgress();
    
    // Tính số liệu 7 ngày gần nhất
    var sheet = getMonthSheet();
    var weekIncome = 0;
    var weekExpense = 0;
    var today = parseInt(Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "d"));
    var startDay = Math.max(1, today - 6);
    
    if (sheet) {
      var lastRow = sheet.getLastRow();
      for (var day = startDay; day <= today; day++) {
        var col = day + 2;
        var data = sheet.getRange(1, 1, lastRow, col).getValues();
        
        for (var i = 1; i < data.length; i++) {
          var catName = String(data[i][0]).toUpperCase().trim();
          var value = Number(data[i][col - 1]) || 0;
          if (value === 0 || !catName) continue;
          if (catName === "TỔNG CHI" || catName === "LỢI NHUẬN" || catName === "CUỐI NGÀY") continue;
          
          var catInfo = CATEGORY_MAP[catName];
          if (!catInfo) continue;
          
          if (catInfo.type === "Thu") weekIncome += value;
          else weekExpense += value;
        }
      }
    }
    
    var lines = [];
    lines.push("📋 BÁO CÁO TUẦN (" + startDay + "-" + today + "/" + (now.getMonth() + 1) + ")");
    lines.push("━━━━━━━━━━━━━━━━━━━━");
    lines.push("");
    
    // Tuần
    lines.push("📊 TUẦN QUA (7 ngày):");
    lines.push("• Thu: " + formatMoney(weekIncome));
    lines.push("• Chi: " + formatMoney(weekExpense));
    lines.push("• Ròng: " + (weekIncome - weekExpense >= 0 ? "+" : "") + formatMoney(weekIncome - weekExpense));
    lines.push("• TB thu/ngày: " + formatMoney(Math.round(weekIncome / 7)));
    lines.push("");
    
    // Tháng (lũy kế)
    lines.push("📅 LŨY KẾ THÁNG " + (now.getMonth() + 1) + ":");
    lines.push("• Thu: " + formatMoney(monthly.totalIncome));
    lines.push("• Chi: " + formatMoney(monthly.totalExpense));
    lines.push("• Ròng: " + (monthly.netCash >= 0 ? "+" : "") + formatMoney(monthly.netCash));
    lines.push("");
    
    // Dự báo
    if (forecast) {
      lines.push("🔮 DỰ BÁO CUỐI THÁNG:");
      lines.push("• Thu: " + formatMoney(forecast.projectedIncome));
      lines.push("• Ròng: " + (forecast.projectedNet >= 0 ? "+" : "") + formatMoney(forecast.projectedNet));
      lines.push("");
    }
    
    // Mục tiêu
    if (goals.length > 0) {
      lines.push("🎯 MỤC TIÊU:");
      goals.forEach(function(g) {
        var filled = Math.min(10, Math.round(g.percent / 10));
        var bar = "";
        for (var i = 0; i < 10; i++) bar += i < filled ? "▓" : "░";
        lines.push("  " + g.status + " " + g.label + " " + bar + " " + g.percent + "%");
      });
      lines.push("");
    }
    
    // Nợ sắp đến hạn
    var upcomingPayments = getNextPayment();
    var urgent = upcomingPayments.filter(function(p) { return p.daysLeft <= 7; });
    if (urgent.length > 0) {
      lines.push("💳 NỢ SẮP ĐẾN HẠN:");
      urgent.forEach(function(p) {
        lines.push("• " + p.name + ": " + formatMoney(p.amount) + " (còn " + p.daysLeft + " ngày)");
      });
      lines.push("");
    }
    
    // Đánh giá
    var weekNet = weekIncome - weekExpense;
    if (weekNet > 3000000) {
      lines.push("🟢 Tuần tốt! Giữ vững nhịp độ.");
    } else if (weekNet > 0) {
      lines.push("🟡 Tuần ổn nhưng cần đẩy mạnh doanh thu.");
    } else {
      lines.push("🔴 Tuần âm! Cần kiểm soát chi tiêu ngay.");
    }
    
    sendMessage(targetChatId, lines.join("\n"));
    
  } catch (e) {
    Logger.log("sendWeeklyReport error: " + e.toString());
    sendMessage(targetChatId, "❌ Lỗi tạo báo cáo tuần: " + e.toString());
  }
}

/**
 * Thiết lập trigger báo cáo tuần (Chủ nhật 20:00)
 */
function setupWeeklyReport() {
  // Xoá trigger cũ
  var triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(function(trigger) {
    if (trigger.getHandlerFunction() === "autoWeeklyReport") {
      ScriptApp.deleteTrigger(trigger);
    }
  });
  
  // Tạo trigger mới: mỗi Chủ nhật lúc 20:00
  ScriptApp.newTrigger("autoWeeklyReport")
    .timeBased()
    .onWeekDay(ScriptApp.WeekDay.SUNDAY)
    .atHour(20)
    .create();
  
  sendMessage(OWNER_CHAT_ID, "✅ Đã thiết lập báo cáo tự động mỗi Chủ nhật 20:00!");
}

function autoWeeklyReport() {
  sendWeeklyReport(OWNER_CHAT_ID);
}

/**
 * Thiết lập báo cáo tự động 8h sáng + 20h tối (giờ Hà Nội)
 * CHẠY HÀM NÀY 1 LẦN
 */
function setupDailyAutoReport() {
  // Xoá trigger cũ
  var triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(function(trigger) {
    var fn = trigger.getHandlerFunction();
    if (fn === "autoDailyMorning" || fn === "autoDailyEvening") {
      ScriptApp.deleteTrigger(trigger);
    }
  });
  
  // Trigger 8h sáng mỗi ngày
  ScriptApp.newTrigger("autoDailyMorning")
    .timeBased()
    .everyDays(1)
    .atHour(8)
    .inTimezone("Asia/Ho_Chi_Minh")
    .create();
  
  // Trigger 20h tối mỗi ngày
  ScriptApp.newTrigger("autoDailyEvening")
    .timeBased()
    .everyDays(1)
    .atHour(20)
    .inTimezone("Asia/Ho_Chi_Minh")
    .create();
  
  sendMessage(OWNER_CHAT_ID, "✅ Đã thiết lập báo cáo tự động:\n• 🌅 8:00 sáng — Briefing ngày mới\n• 🌙 20:00 tối — Tổng kết ngày\n\n(Giờ Hà Nội, chạy mỗi ngày)");
}

/**
 * Báo cáo buổi sáng (8h) - Nhắc nhở & kế hoạch ngày
 */
function autoDailyMorning() {
  try {
    var now = new Date();
    var lines = [];
    lines.push("🌅 CHÀO BUỔI SÁNG " + Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "dd/MM/yyyy"));
    lines.push("━━━━━━━━━━━━━━━━━━━━");
    lines.push("");
    
    // Mục tiêu hôm nay
    lines.push("🎯 MỤC TIÊU HÔM NAY:");
    lines.push("• Doanh thu tối thiểu: " + formatMoney(BUSINESS.targetDailyRevenue));
    lines.push("• Tích lũy tối thiểu: " + formatMoney(BUSINESS.targetDailyAccumulation));
    lines.push("");
    
    // Nợ sắp đến hạn
    var upcomingPayments = getNextPayment();
    var urgent = upcomingPayments.filter(function(p) { return p.daysLeft <= 5; });
    if (urgent.length > 0) {
      lines.push("🚨 NỢ SẮP ĐẾN HẠN:");
      urgent.forEach(function(p) {
        lines.push("• " + p.name + ": " + formatMoney(p.amount) + " (còn " + p.daysLeft + " ngày)");
      });
      lines.push("");
    }
    
    // Tiến độ tháng
    var monthly = getMonthlySummary();
    var today = parseInt(Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "d"));
    var monthStr = Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "M");
    var yearStr = Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "yyyy");
    var daysInMonth = new Date(parseInt(yearStr), parseInt(monthStr), 0).getDate();
    var dayPercent = Math.round(today / daysInMonth * 100);
    var incomePercent = BUSINESS.targetDailyRevenue * daysInMonth > 0 ? Math.round(monthly.totalIncome / (BUSINESS.targetDailyRevenue * daysInMonth) * 100) : 0;
    
    lines.push("📊 TIẾN ĐỘ THÁNG (" + dayPercent + "% thời gian):");
    lines.push("• Thu: " + formatMoney(monthly.totalIncome) + " (" + incomePercent + "% target)");
    lines.push("• Chi: " + formatMoney(monthly.totalExpense));
    lines.push("");
    
    // Mục tiêu chi tiêu
    var goals = checkGoalProgress();
    if (goals.length > 0) {
      goals.forEach(function(g) {
        if (g.percent > 80) {
          lines.push("⚠️ " + g.label + ": " + g.percent + "% budget (cẩn thận!)");
        }
      });
    }
    
    // Haravan - Doanh thu hôm qua
    try {
      if (HARAVAN_TOKEN !== "DÁN_HARAVAN_TOKEN_VÀO_ĐÂY") {
        var todayStr = Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "yyyy-MM-dd");
        var todayDateHanoi = new Date(todayStr + "T00:00:00+07:00");
        var yesterdayDateHanoi = new Date(todayDateHanoi.getTime() - 24*60*60*1000);
        
        var ydMin = Utilities.formatDate(yesterdayDateHanoi, "Asia/Ho_Chi_Minh", "yyyy-MM-dd'T'00:00:00'+07:00'");
        var ydMax = Utilities.formatDate(yesterdayDateHanoi, "Asia/Ho_Chi_Minh", "yyyy-MM-dd'T'23:59:59'+07:00'");
        var ydOrders = getHaravanOrders({financial_status: "paid", created_at_min: ydMin, created_at_max: ydMax, limit: 250});
        var ydRevenue = 0;
        ydOrders.forEach(function(o) { ydRevenue += Number(o.total_price) || 0; });
        
        lines.push("📦 HARAVAN HÔM QUA:");
        lines.push("  ✅ " + ydOrders.length + " đơn — " + formatMoney(ydRevenue));
        lines.push("");
        
        // Sync đơn hôm nay luôn
        syncHaravanRevenue();
      }
    } catch(hErr) { Logger.log("Morning haravan error: " + hErr); }
    
    lines.push("💪 Chúc một ngày làm việc hiệu quả!");
    
    sendMessage(OWNER_CHAT_ID, lines.join("\n"));
    
    // Kiểm tra nhắc nhở tuỳ chỉnh
    checkCustomReminders();
  } catch (e) {
    Logger.log("autoDailyMorning error: " + e.toString());
  }
}

/**
 * Báo cáo buổi tối (20h) - Tổng kết ngày
 */
function autoDailyEvening() {
  try {
    // Sync Haravan trước khi báo cáo
    var haravanMsg = "";
    try {
      if (HARAVAN_TOKEN !== "DÁN_HARAVAN_TOKEN_VÀO_ĐÂY") {
        var syncResult = syncHaravanRevenue();
        var stats = getHaravanStats();
        var hvLines = [];
        hvLines.push("");
        hvLines.push("📦 HARAVAN HÔM NAY:");
        hvLines.push("  📥 Tổng: " + stats.todayTotal + " đơn");
        hvLines.push("  ✅ Đã TT: " + stats.todayPaid + " (" + formatMoney(stats.todayRevenue) + ")");
        if (stats.todayPending > 0) hvLines.push("  ⏳ Chờ: " + stats.todayPending + " (" + formatMoney(stats.todayPendingRevenue) + ")");
        if (syncResult.success && syncResult.orders > 0) {
          hvLines.push("  🔄 Sync: +" + syncResult.orders + " đơn mới");
        }
        haravanMsg = hvLines.join("\n");
      }
    } catch(hErr) { Logger.log("Evening haravan error: " + hErr); }
    
    // Gửi báo cáo ngày
    sendDailyReport(OWNER_CHAT_ID);
    
    // Gửi thêm phần Haravan
    if (haravanMsg) {
      sendMessage(OWNER_CHAT_ID, haravanMsg);
    }
    
    // Kiểm tra budget alerts
    checkBudgetAlerts();
    
  } catch (e) {
    Logger.log("autoDailyEvening error: " + e.toString());
  }
}

/**
 * Quản lý user - Thêm/xoá user
 */
function handleUserCommand(chatId, parts) {
  // Chỉ owner mới được quản lý user
  if (String(chatId) !== OWNER_CHAT_ID) {
    sendMessage(chatId, "⛔ Chỉ chủ bot mới có quyền quản lý user.");
    return;
  }
  
  if (parts.length < 2) {
    var lines = [];
    lines.push("👥 QUẢN LÝ USER");
    lines.push("━━━━━━━━━━━━━━━━━━━━");
    lines.push("");
    lines.push("User hiện tại:");
    ALLOWED_USERS.forEach(function(uid, idx) {
      var label = uid === OWNER_CHAT_ID ? " (Owner)" : "";
      lines.push("  " + (idx + 1) + ". " + uid + label);
    });
    lines.push("");
    lines.push("Thêm user: /user add [chatId]");
    lines.push("Xoá user: /user del [chatId]");
    lines.push("");
    lines.push("💡 Người muốn dùng bot cần gửi /start cho bot trước.");
    sendMessage(chatId, lines.join("\n"));
    return;
  }
  
  var action = parts[1].toLowerCase();
  var targetId = parts[2] || "";
  
  if (action === "add" && targetId) {
    if (ALLOWED_USERS.indexOf(targetId) === -1) {
      ALLOWED_USERS.push(targetId);
      // Lưu vào Properties để persist
      PropertiesService.getScriptProperties().setProperty("allowed_users", JSON.stringify(ALLOWED_USERS));
      sendMessage(chatId, "✅ Đã thêm user: " + targetId);
      sendMessage(targetId, "🎉 Bạn đã được thêm vào bot quản lý tài chính! Gõ /help để bắt đầu.");
    } else {
      sendMessage(chatId, "ℹ️ User đã tồn tại.");
    }
  } else if (action === "del" && targetId) {
    if (targetId === OWNER_CHAT_ID) {
      sendMessage(chatId, "❌ Không thể xoá owner!");
      return;
    }
    ALLOWED_USERS = ALLOWED_USERS.filter(function(uid) { return uid !== targetId; });
    PropertiesService.getScriptProperties().setProperty("allowed_users", JSON.stringify(ALLOWED_USERS));
    sendMessage(chatId, "✅ Đã xoá user: " + targetId);
  }
}

/**
 * Web Mini Dashboard - Trả về HTML khi truy cập URL
 */
function doGet(e) {
  var html = getDashboardHtml();
  return HtmlService.createHtmlOutput(html)
    .setTitle("💰 Financial Dashboard")
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

/**
 * Webhook nhận dữ liệu từ Haravan (Real-time)
 */
function doPost(e) {
  if (!e || !e.postData) return ContentService.createTextOutput("No data");
  
  try {
    var data = JSON.parse(e.postData.contents);
    
    // Check if it's a Haravan order
    if (data.id && (data.order_number || data.total_price)) {
      handleHaravanWebhook(data);
    }
    
    // Check if it's a Casso webhook (Ngân hàng)
    // Format: { error: 0, data: [...] }
    if (data.error === 0 && Array.isArray(data.data)) {
      handleCassoWebhook(data.data);
    }
    
  } catch (err) {
    Logger.log("doPost error: " + err);
  }
  
  return ContentService.createTextOutput("OK");
}

/**
 * Xử lý webhook từ Casso (Ngân hàng)
 */
function handleCassoWebhook(transactions) {
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(10000);
    
    var now = new Date();
    var todayStr = Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "yyyy-MM-dd");
    var syncedKey = "casso_synced_" + todayStr;
    var props = PropertiesService.getScriptProperties();
    var syncedJson = props.getProperty(syncedKey) || "[]";
    var alreadySynced = JSON.parse(syncedJson);
    
    transactions.forEach(function(trans) {
      var tid = String(trans.tid); // Mã giao dịch unique
      if (alreadySynced.indexOf(tid) !== -1) return; // Đã sync
      
      var amount = Number(trans.amount);
      var content = trans.description;
      var type = amount > 0 ? "Thu" : "Chi";
      var absAmount = Math.abs(amount);
      
      // Phân loại giao dịch bằng AI (Gemini) hoặc quy tắc
      var category = "Chi tiêu khác";
      if (type === "Thu") {
        category = "Thu nhập khác";
        // Nếu nội dung chứa mã đơn hàng Haravan -> "Bán hàng"
        if (content.match(/DH\d+/i) || content.match(/#\d+/)) {
          category = "Bán hàng";
        }
      } else {
        // Dùng Gemini đoán danh mục chi tiêu
        try {
          var prompt = "Phân loại giao dịch ngân hàng sau vào 1 trong các nhóm: " + 
            "Ăn uống, Cafe, Phụ phí, Ads, Tiền nhà, Trả nợ, Lương NV, Mua sắm. " +
            "Chỉ trả về tên nhóm chính xác, không giải thích. " +
            "Nội dung: \"" + content + "\". Số tiền: " + absAmount;
          
          var aiCat = callGemini(prompt, "Bạn là trợ lý phân loại tài chính. Chỉ trả về từ khoá ngắn gọn.");
          if (aiCat && BOT_TO_SHEET[aiCat]) {
            category = aiCat;
          } else {
            // Fallback rules
            if (content.match(/CIRCLE K|WINMART|7-ELEVEN/i)) category = "Ăn uống";
            else if (content.match(/GRAB|BE|GOJEK/i)) category = "Phụ phí";
            else if (content.match(/FACEBOOK|GOOGLE/i)) category = "Ads";
            else if (content.match(/VIETCOMBANK|VCB|LÃI/i)) category = "Trả nợ";
          }
        } catch (aiErr) {
          Logger.log("AI categorize error: " + aiErr);
        }
      }
      
      // Ghi vào Sheet
      logTransaction(content, absAmount, type, category);
      
      // Cập nhật danh sách đã sync
      alreadySynced.push(tid);
      
      // Báo Telegram
      var icon = type === "Thu" ? "💰" : "💸";
      var msg = icon + " GD NGÂN HÀNG:\n" +
        formatMoney(absAmount) + " (" + type + ")\n" +
        "📝 " + content + "\n" +
        "📂 Phân loại: " + category;
      sendMessage(OWNER_CHAT_ID, msg);
    });
    
    props.setProperty(syncedKey, JSON.stringify(alreadySynced));
    
  } catch (e) {
    Logger.log("Casso webhook error: " + e);
  } finally {
    lock.releaseLock();
  }
}

function handleHaravanWebhook(order) {
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(10000); // Chờ lock tránh xung đột ghi Sheet
    
    // Bỏ qua đơn huỷ
    if (order.cancelled_at) return;
    
    // Check Mode (paid vs all)
    if (typeof HARAVAN_SYNC_MODE !== 'undefined' && HARAVAN_SYNC_MODE === 'paid') {
      if (order.financial_status !== 'paid') return;
    }
    
    // Check deduplication
    var now = new Date();
    var todayStr = Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "yyyy-MM-dd");
    var syncedKey = "haravan_synced_" + todayStr;
    var props = PropertiesService.getScriptProperties();
    var syncedJson = props.getProperty(syncedKey) || "[]";
    var alreadySynced = JSON.parse(syncedJson);
    var orderId = String(order.id);
    
    if (alreadySynced.indexOf(orderId) !== -1) return; // Đã sync rồi
    
    // Process
    var amount = Number(order.total_price) || 0;
    if (amount <= 0) return;
    
    // Log to Sheet
    logTransaction("Haravan #" + order.order_number, amount, "Thu", HARAVAN_REVENUE_CATEGORY);
    
    // Update Sync List
    alreadySynced.push(orderId);
    props.setProperty(syncedKey, JSON.stringify(alreadySynced));
    
    // Update Stats
    var statsKey = "haravan_stats_" + todayStr;
    var prevStats = JSON.parse(props.getProperty(statsKey) || '{"orders":0,"revenue":0}');
    prevStats.orders += 1;
    prevStats.revenue += amount;
    props.setProperty(statsKey, JSON.stringify(prevStats));
    
    // Notify Telegram
    var msg = "🔔 ĐƠN MỚI HARAVAN (Real-time)\n" +
      "#" + order.order_number + " - " + formatMoney(amount) + "\n" +
      "👤 " + (order.customer ? (order.customer.first_name + " " + order.customer.last_name) : "Khách") + "\n" +
      "💰 Đã ghi vào Sheet!";
    sendMessage(OWNER_CHAT_ID, msg);
    
  } catch (e) {
    Logger.log("Webhook error: " + e);
  } finally {
    lock.releaseLock();
  }
}

function registerHaravanWebhook() {
  if (HARAVAN_TOKEN.indexOf("DÁN_") !== -1) {
    Logger.log("Chưa cấu hình Token");
    return;
  }
  
  var scriptUrl = ScriptApp.getService().getUrl();
  if (!scriptUrl) {
    Logger.log("Chưa có URL");
    sendMessage(OWNER_CHAT_ID, "⚠️ Cần Deploy Web App trước khi đăng ký Webhook!");
    return;
  }
  
  var topics = ["orders/create", "orders/updated"];
  
  topics.forEach(function(topic) {
    var payload = {
      "webhook": {
        "topic": topic,
        "address": scriptUrl,
        "format": "json"
      }
    };
    
    var url = HARAVAN_API_BASE + "/webhooks.json";
    var options = {
      method: "post",
      headers: {"Authorization": "Bearer " + HARAVAN_TOKEN, "Content-Type": "application/json"},
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    };
    
    var resp = UrlFetchApp.fetch(url, options);
    Logger.log("Register " + topic + ": " + resp.getContentText());
  });
  
  sendMessage(OWNER_CHAT_ID, "✅ Đã đăng ký Webhook Haravan (Real-time) thành công!\nURL: " + scriptUrl);
}

function getDashboardHtml() {
  var monthly = getMonthlySummary();
  var forecast = getCashFlowForecast();
  var goals = checkGoalProgress();
  var risk = checkCashFlowRisk();
  var now = new Date();
  var monthName = "Tháng " + Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "M/yyyy");
  
  // Category data for chart
  var cats = monthly.categoryBreakdown || {};
  var catLabels = JSON.stringify(Object.keys(cats));
  var catValues = JSON.stringify(Object.keys(cats).map(function(k) { return cats[k]; }));
  
  var totalDebt = DEBTS.reduce(function(s,d){return s+d.balance;}, 0);
  
  var html = '<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">' +
    '<title>Financial Dashboard</title>' +
    '<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>' +
    '<style>' +
    '* { margin: 0; padding: 0; box-sizing: border-box; }' +
    'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: #fff; min-height: 100vh; padding: 20px; }' +
    'h1 { text-align: center; font-size: 1.5em; margin-bottom: 20px; background: linear-gradient(90deg, #00d2ff, #3a7bd5); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }' +
    '.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; max-width: 1200px; margin: 0 auto; }' +
    '.card { background: rgba(255,255,255,0.08); backdrop-filter: blur(10px); border-radius: 16px; padding: 20px; border: 1px solid rgba(255,255,255,0.1); }' +
    '.card h2 { font-size: 1em; margin-bottom: 12px; opacity: 0.8; }' +
    '.big-number { font-size: 2em; font-weight: 700; }' +
    '.green { color: #4ade80; } .red { color: #f87171; } .yellow { color: #fbbf24; } .blue { color: #60a5fa; }' +
    '.stat-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }' +
    '.progress-bar { height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; margin-top: 6px; }' +
    '.progress-fill { height: 100%; border-radius: 4px; transition: width 0.3s; }' +
    '.debt-item { padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }' +
    '.debt-name { font-weight: 600; }' +
    '.debt-amount { color: #f87171; }' +
    'canvas { max-height: 250px; }' +
    '.updated { text-align: center; opacity: 0.4; font-size: 0.8em; margin-top: 20px; }' +
    '</style></head><body>' +
    '<h1>💰 FINANCIAL DASHBOARD - ' + monthName + '</h1>' +
    '<div class="grid">';
  
  // Card 1: Thu Chi
  var netClass = monthly.netCash >= 0 ? 'green' : 'red';
  html += '<div class="card"><h2>📊 Thu Chi Tháng Này</h2>' +
    '<div class="stat-row"><span>Thu nhập</span><span class="green">' + formatMoneyFull(monthly.totalIncome) + '</span></div>' +
    '<div class="stat-row"><span>Chi tiêu</span><span class="red">' + formatMoneyFull(monthly.totalExpense) + '</span></div>' +
    '<div class="stat-row"><span>Ròng</span><span class="' + netClass + ' big-number">' + (monthly.netCash >= 0 ? '+' : '') + formatMoneyFull(monthly.netCash) + '</span></div>' +
    '</div>';
  
  // Card 2: Dự báo
  if (forecast) {
    var fNetClass = forecast.projectedNet >= 0 ? 'green' : 'red';
    html += '<div class="card"><h2>🔮 Dự Báo Cuối Tháng</h2>' +
      '<div class="stat-row"><span>Ngày</span><span>' + forecast.today + '/' + forecast.daysInMonth + ' (còn ' + forecast.daysLeft + ' ngày)</span></div>' +
      '<div class="stat-row"><span>Thu dự kiến</span><span class="green">' + formatMoneyFull(forecast.projectedIncome) + '</span></div>' +
      '<div class="stat-row"><span>Chi dự kiến</span><span class="red">' + formatMoneyFull(forecast.projectedExpense) + '</span></div>' +
      '<div class="stat-row"><span>Ròng dự kiến</span><span class="' + fNetClass + '">' + (forecast.projectedNet >= 0 ? '+' : '') + formatMoneyFull(forecast.projectedNet) + '</span></div>' +
      '</div>';
  }
  
  // Card 3: Tổng nợ
  html += '<div class="card"><h2>💳 Tổng Nợ</h2>' +
    '<div class="big-number red">' + formatMoneyFull(totalDebt) + '</div>';
  DEBTS.forEach(function(d) {
    if (d.balance > 0) {
      var debtPercent = Math.round(d.balance / totalDebt * 100);
      html += '<div class="debt-item"><div class="stat-row"><span class="debt-name">' + d.fullName + '</span><span class="debt-amount">' + formatMoneyFull(d.balance) + '</span></div>' +
        '<div class="progress-bar"><div class="progress-fill" style="width:' + debtPercent + '%;background:#f87171;"></div></div></div>';
    }
  });
  html += '</div>';
  
  // Card 4: Mục tiêu
  if (goals.length > 0) {
    html += '<div class="card"><h2>🎯 Mục Tiêu Chi Tiêu</h2>';
    goals.forEach(function(g) {
      var gColor = g.percent >= 100 ? '#f87171' : g.percent > 80 ? '#fbbf24' : '#4ade80';
      html += '<div class="stat-row"><span>' + g.label + '</span><span>' + formatMoneyFull(g.spent) + ' / ' + formatMoneyFull(g.limit) + '</span></div>' +
        '<div class="progress-bar"><div class="progress-fill" style="width:' + Math.min(100, g.percent) + '%;background:' + gColor + ';"></div></div>';
    });
    html += '</div>';
  }
  
  // Card 5: Biểu đồ
  html += '<div class="card" style="grid-column: span 2"><h2>📊 Phân Bổ Chi Tiêu</h2>' +
    '<canvas id="spendingChart"></canvas></div>';
  
  // Card 6: Rủi ro
  var riskColor = risk.riskLevel && risk.riskLevel.indexOf('AN TOÀN') >= 0 ? 'green' : 
                  risk.riskLevel && risk.riskLevel.indexOf('SÁT NÚT') >= 0 ? 'yellow' : 'red';
  html += '<div class="card"><h2>⚠️ Rủi Ro Dòng Tiền</h2>' +
    '<div class="big-number ' + riskColor + '">' + (risk.riskLevel || 'N/A') + '</div>' +
    '<p style="margin-top:10px;opacity:0.7">' + (risk.message || '') + '</p></div>';
  
  html += '</div>'; // close grid
  
  // Chart.js script
  html += '<script>' +
    'var ctx = document.getElementById("spendingChart").getContext("2d");' +
    'var labels = ' + catLabels + ';' +
    'var values = ' + catValues + ';' +
    'var colors = ["#FF6384","#36A2EB","#FFCE56","#4BC0C0","#9966FF","#FF9F40","#FF6384","#C9CBCF","#4ade80","#f87171"];' +
    'new Chart(ctx, {' +
    '  type: "doughnut",' +
    '  data: { labels: labels, datasets: [{ data: values, backgroundColor: colors.slice(0, labels.length), borderWidth: 0 }] },' +
    '  options: { responsive: true, plugins: { legend: { position: "right", labels: { color: "#fff", font: { size: 11 } } } } }' +
    '});' +
    '</script>';
  
  html += '<p class="updated">Cập nhật: ' + Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "dd/MM/yyyy HH:mm") + '</p>';
  html += '</body></html>';
  
  return html;
}

/**
 * Hàm test - Gọi thủ công để kiểm tra
 */
function testBot() {
  // Test 1: Gửi tin nhắn
  var testMsg = "🤖 Bot đang hoạt động! (Test gửi tin)";
  sendMessage(OWNER_CHAT_ID, testMsg);
  
  try {
    // Test 2: Đọc dữ liệu từ Sheet (Kiểm tra quyền truy cập)
    var summary = getDailySummary();
    Logger.log("✅ Truy cập Sheet thành công: " + JSON.stringify(summary));
    sendMessage(OWNER_CHAT_ID, "✅ Truy cập Sheet thành công! Tổng thu hôm nay: " + summary.totalIncome);
  } catch (e) {
    Logger.log("❌ Lỗi truy cập Sheet: " + e.toString());
    sendMessage(OWNER_CHAT_ID, "❌ Lỗi truy cập Sheet: " + e.toString());
  }
}

/**
 * ============================================================
 * POLLING MODE - Thay thế Webhook (ổn định hơn)
 * ============================================================
 * Bot tự kiểm tra tin nhắn mới mỗi phút thay vì chờ Telegram gửi.
 * Cách dùng:
 *   1. Chạy hàm setupPolling() MỘT LẦN để thiết lập
 *   2. Bot sẽ tự động chạy mỗi phút
 *   3. Để dừng: chạy stopPolling()
 */

/**
 * Kiểm tra và xử lý tin nhắn mới từ Telegram
 * Hàm này được trigger tự động mỗi phút
 */
function pollUpdates() {
  // Dùng Lock để chỉ cho 1 instance chạy tại 1 thời điểm
  var lock = LockService.getScriptLock();
  var hasLock = lock.tryLock(5000); // Đợi tối đa 5 giây
  if (!hasLock) {
    Logger.log("⏭ pollUpdates: Đang có instance khác chạy, bỏ qua.");
    return;
  }
  
  try {
    var props = PropertiesService.getScriptProperties();
    var lastUpdateId = parseInt(props.getProperty("lastUpdateId") || "0");
    var cache = CacheService.getScriptCache();
    
    // Gọi getUpdates API
    var url = "https://api.telegram.org/bot" + TELEGRAM_TOKEN + "/getUpdates?timeout=0&limit=10";
    if (lastUpdateId > 0) {
      url += "&offset=" + (lastUpdateId + 1);
    }
    
    var response = UrlFetchApp.fetch(url, {muteHttpExceptions: true});
    var data = JSON.parse(response.getContentText());
    
    if (!data.ok || !data.result || data.result.length === 0) {
      lock.releaseLock();
      return;
    }
    
    // Xử lý từng tin nhắn
    data.result.forEach(function(update) {
      // Cập nhật lastUpdateId NGAY LẬP TỨC để tránh xử lý lại
      lastUpdateId = update.update_id;
      props.setProperty("lastUpdateId", String(lastUpdateId));
      
      try {
        // Dedup bằng CacheService
        var updateKey = "upd_" + update.update_id;
        if (cache.get(updateKey)) {
          Logger.log("⏭ Bỏ qua update trùng: " + update.update_id);
          return;
        }
        cache.put(updateKey, "1", 600);
        
        var chatId = String(update.message.chat.id);
        
        // Kiểm tra quyền truy cập (multi-user)
        if (ALLOWED_USERS.indexOf(chatId) === -1) {
          sendMessage(chatId, "⛔ Bạn không có quyền sử dụng bot này.\nChat ID: " + chatId);
          return;
        }
        
        // Xử lý tin nhắn TEXT
        if (update.message.text) {
          var userText = update.message.text.trim();
          Logger.log("📩 Nhận tin nhắn: " + userText + " từ chatId: " + chatId);
          
          if (userText.startsWith("/")) {
            handleCommand(chatId, userText);
          } else {
            processMessage(chatId, userText);
          }
        }
        // Xử lý ẢNH (nhận diện bill)
        else if (update.message.photo) {
          Logger.log("📷 Nhận ảnh từ chatId: " + chatId);
          processPhoto(chatId, update.message);
        }
        // Xử lý GIỌNG NÓI (Voice Input)
        else if (update.message.voice) {
          Logger.log("🎤 Nhận voice từ chatId: " + chatId);
          processVoice(chatId, update.message);
        }
      } catch (msgError) {
        Logger.log("❌ Lỗi xử lý tin nhắn: " + msgError.toString());
        try {
          sendMessage(OWNER_CHAT_ID, "❌ Lỗi khi xử lý: " + msgError.toString());
        } catch(e) {}
      }
    });
    
  } catch (error) {
    Logger.log("pollUpdates error: " + error.toString());
    try {
      var errorUrl = "https://api.telegram.org/bot" + TELEGRAM_TOKEN + "/sendMessage";
      UrlFetchApp.fetch(errorUrl, {
        method: "post",
        contentType: "application/json",
        payload: JSON.stringify({chat_id: OWNER_CHAT_ID, text: "❌ Poll error: " + error.toString()}),
        muteHttpExceptions: true
      });
    } catch(e) {}
  } finally {
    lock.releaseLock();
  }
}

/**
 * Thiết lập Polling - CHẠY HÀM NÀY 1 LẦN
 * Tạo trigger tự động chạy pollUpdates mỗi phút
 */
function setupPolling() {
  // 1. Xoá webhook cũ (nếu có)
  var deleteUrl = "https://api.telegram.org/bot" + TELEGRAM_TOKEN + "/deleteWebhook?drop_pending_updates=true";
  UrlFetchApp.fetch(deleteUrl, {muteHttpExceptions: true});
  Logger.log("✅ Đã xoá webhook cũ");
  
  // 2. Xoá tất cả trigger cũ tên pollUpdates
  var triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(function(trigger) {
    if (trigger.getHandlerFunction() === "pollUpdates") {
      ScriptApp.deleteTrigger(trigger);
    }
  });
  Logger.log("✅ Đã xoá trigger cũ");
  
  // 3. Tạo trigger mới: chạy pollUpdates mỗi phút
  ScriptApp.newTrigger("pollUpdates")
    .timeBased()
    .everyMinutes(1)
    .create();
  Logger.log("✅ Đã tạo trigger mới: pollUpdates mỗi 1 phút");
  
  // 4. Reset lastUpdateId để bắt đầu từ tin nhắn mới nhất
  var url = "https://api.telegram.org/bot" + TELEGRAM_TOKEN + "/getUpdates?offset=-1&limit=1";
  var response = UrlFetchApp.fetch(url, {muteHttpExceptions: true});
  var data = JSON.parse(response.getContentText());
  if (data.ok && data.result && data.result.length > 0) {
    var latestId = data.result[data.result.length - 1].update_id;
    PropertiesService.getScriptProperties().setProperty("lastUpdateId", String(latestId));
    Logger.log("✅ Reset lastUpdateId = " + latestId);
  }
  
  // 5. Gửi thông báo
  sendMessage(OWNER_CHAT_ID, "🤖 Bot đã được thiết lập chế độ Polling!\n\nBot sẽ kiểm tra tin nhắn mới mỗi phút.\nHãy thử gõ /bc hoặc /no để test!");
  Logger.log("🎉 Setup Polling hoàn tất! Bot sẽ tự động kiểm tra tin nhắn mỗi phút.");
}

/**
 * Dừng Polling - Chạy hàm này nếu muốn tắt bot
 */
function stopPolling() {
  var triggers = ScriptApp.getProjectTriggers();
  var count = 0;
  triggers.forEach(function(trigger) {
    if (trigger.getHandlerFunction() === "pollUpdates") {
      ScriptApp.deleteTrigger(trigger);
      count++;
    }
  });
  Logger.log("✅ Đã xoá " + count + " trigger. Bot đã dừng.");
  sendMessage(OWNER_CHAT_ID, "⏹ Bot đã dừng hoạt động.");
}

/**
 * Xử lý tin nhắn thoại (Voice)
 */
function processVoice(chatId, message) {
  try {
    var voice = message.voice;
    var fileId = voice.file_id;
    var mimeType = voice.mime_type || "audio/ogg";
    
    sendMessage(chatId, "🎤 Đang nghe và phân tích...");
    
    // 1. Lấy đường dẫn file từ Telegram API
    var fileRes = UrlFetchApp.fetch("https://api.telegram.org/bot" + TELEGRAM_TOKEN + "/getFile?file_id=" + fileId);
    var filePath = JSON.parse(fileRes.getContentText()).result.file_path;
    
    // 2. Tải file về (Blob)
    var audioBlob = UrlFetchApp.fetch("https://api.telegram.org/file/bot" + TELEGRAM_TOKEN + "/" + filePath).getBlob();
    var base64 = Utilities.base64Encode(audioBlob.getBytes());
    
    // 3. Gửi cho Gemini Multimodal
    var prompt = "Nghe đoạn ghi âm này và trích xuất giao dịch tài chính nếu có. " +
      "Trả về định dạng text duy nhất: 'Nội dung số tiền'. Ví dụ: 'Cafe 50k'. " +
      "Nếu là lệnh tra cứu, hãy trả về lệnh tương ứng (VD: 'Báo cáo tháng' -> '/thang'). " +
      "Nếu không nghe rõ hoặc không liên quan tài chính, trả về 'KHÔNG_RÕ'. " +
      "Chỉ trả về kết quả, không giải thích.";
      
    var result = callGeminiMultimodal(prompt, mimeType, base64);
    
    if (result && result.indexOf("KHÔNG_RÕ") === -1) {
      sendMessage(chatId, "🗣 Voice: " + result);
      
      // Xử lý kết quả như tin nhắn text
      if (result.startsWith("/")) {
        handleCommand(chatId, result);
      } else {
        processMessage(chatId, result);
      }
    } else {
      sendMessage(chatId, "❌ Không nghe rõ giao dịch hoặc nội dung không liên quan.");
    }
    
  } catch (e) {
    Logger.log("processVoice error: " + e);
    sendMessage(chatId, "❌ Lỗi xử lý voice: " + e.message);
  }
}

/**
 * Gọi Gemini Multimodal (Text + Image/Audio)
 */
function callGeminiMultimodal(prompt, mimeType, dataBase64) {
  var url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=" + GEMINI_API_KEY;
  
  var payload = {
    "contents": [{
      "parts": [
        {"text": prompt},
        {
          "inline_data": {
            "mime_type": mimeType,
            "data": dataBase64
          }
        }
      ]
    }],
    "generationConfig": {
      "temperature": 0.1,
      "maxOutputTokens": 1024
    }
  };
  
  var options = {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };
  
  try {
    var response = UrlFetchApp.fetch(url, options);
    var json = JSON.parse(response.getContentText());
    
    if (json.candidates && json.candidates[0] && json.candidates[0].content) {
      return json.candidates[0].content.parts[0].text.trim();
    }
    
    Logger.log("Gemini Multimodal error: " + response.getContentText());
    return null;
  } catch (error) {
    Logger.log("Gemini API error: " + error.toString());
    return null;
  }
}

/**
 * AI Phân Tích Sâu (Level 6)
 * Đọc toàn bộ dữ liệu Sheet tháng -> CSV -> Gemini
 */
function generateMonthlyAnalysis(chatId, monthArg) {
  try {
    var sheet;
    var monthLabel;
    
    if (monthArg) {
       // Xử lý chuỗi tháng nhập vào (VD: 02, 02-2026)
       var parts = monthArg.match(/(\d{1,2})([-./]?(\d{4}))?/);
       if (parts) {
         var m = parseInt(parts[1]);
         var now = new Date();
         var currentYear = parseInt(Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "yyyy"));
         var y = parts[3] ? parseInt(parts[3]) : currentYear;
         var targetDate = new Date(y, m - 1, 1);
         sheet = getMonthSheet(targetDate);
         monthLabel = (m < 10 ? "0"+m : m) + "/" + y;
       }
    } else {
       sheet = getMonthSheet(); // Tháng hiện tại
       var now = new Date();
       monthLabel = Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "M/yyyy");
    }

    if (!sheet) {
      sendMessage(chatId, "❌ Không tìm thấy dữ liệu tháng " + (monthArg || "này"));
      return;
    }
    
    sendMessage(chatId, "🤖 Đang đọc dữ liệu tháng " + monthLabel + " và suy nghĩ... (Đợi ~15s)");
    
    // Extract Matrix Data
    // Layout: Row 1 = Headers (Days), Col 1 = Categories (Rows)
    var data = sheet.getDataRange().getValues();
    var transactions = [];
    
    // Header Row (Row 1 -> index 0)
    var headers = data[0];
    
    for (var r = 1; r < data.length; r++) {
      var category = String(data[r][0]).trim();
      if (!category || category === "TỔNG THU" || category === "TỔNG CHI" || category === "LỢI NHUẬN") continue;
      
      var catInfo = CATEGORY_MAP[category.toUpperCase()];
      var type = catInfo ? catInfo.type : (category.indexOf("THU") >= 0 ? "Thu" : "Chi");
      
      for (var c = 1; c < headers.length; c++) {
        var day = headers[c]; // Có thể là số ngày (1, 2...) hoặc Date object
        var amount = data[r][c];
        
        if (typeof amount === 'number' && amount !== 0) {
           var dateStr = day;
           if (day instanceof Date) dateStr = day.getDate();
           
           transactions.push({
             date: dateStr + "/" + monthLabel,
             category: category,
             amount: amount,
             type: type
           });
        }
      }
    }
    
    if (transactions.length === 0) {
      sendMessage(chatId, "⚠️ Tháng này chưa có giao dịch nào để phân tích.");
      return;
    }
    
    // Sort transactions by Date
    transactions.sort(function(a, b) {
      return parseInt(a.date) - parseInt(b.date);
    });
    
    // Convert to CSV
    var csv = "Ngày,Danh mục,Số tiền,Loại\n" + 
      transactions.map(function(t) { return t.date + "," + t.category + "," + t.amount + "," + t.type; }).join("\n");
      
    // Call Gemini
    var prompt = "Bạn là chuyên gia tài chính cá nhân. Hãy phân tích bảng dữ liệu chi tiêu CSV dưới đây của tháng " + monthLabel + ":\n\n" +
      csv + "\n\n" +
      "Yêu cầu output (Markdown):\n" +
      "1. **Tổng quan**: Tổng Thu, Tổng Chi, Số dư hiện tại.\n" +
      "2. **Top Chi tiêu**: 3 khoản tốn kém nhất (kèm % nếu được).\n" +
      "3. **Xu hướng**: Chỉ ra các ngày tiêu nhiều bất thường hoặc thói quen xấu (VD: đi cafe quá nhiều).\n" +
      "4. **Lời khuyên**: Gợi ý cắt giảm cụ thể để tiết kiệm hơn vào tháng sau.\n" +
      "Hãy nhận xét thẳng thắn, giọng điệu như một người bạn thân.";
      
    // Dùng model Pro 1.5 cho phân tích sâu
    var analysis = callGemini(prompt, "Bạn là trợ lý tài chính thông minh, sắc sảo.", GEMINI_MODEL_SMART);
    
    if (analysis) {
      sendMessage(chatId, "📊 *BÁO CÁO PHÂN TÍCH THÁNG " + monthLabel + "*\n\n" + analysis);
    } else {
      sendMessage(chatId, "❌ Gemini không phản hồi. Thử lại sau.");
    }

  } catch (e) {
    Logger.log("generateMonthlyAnalysis error: " + e);
    sendMessage(chatId, "❌ Lỗi phân tích: " + e.message);
  }
}

/**
 * Level 7: Mô phỏng tài chính (/sim)
 */
function handleSimulationCommand(chatId, args) {
  var content = args.join(" ").trim();
  if (!content) {
    sendMessage(chatId, "📉 Cách dùng: `/sim [số tiền] [nội dung]`\nVí dụ: `/sim 500k mua điện thoại` hoặc `/sim +10tr lương`");
    return;
  }
  
  // Parse inputs
  var amount = 0;
  var description = "";
  
  // Regex bắt số tiền (500k, 1.5tr, 10m...)
  var amMatch = content.match(/([+\-]?\d+[\.,]?\d*[kKmMđĐuU$]*)/);
  if (amMatch) {
    var rawAm = amMatch[0];
    amount = parseMoney(rawAm);
    description = content.replace(rawAm, "").trim();
  }
  
  if (amount === 0) {
    sendMessage(chatId, "❌ Không hiểu số tiền. Hãy nhập ví dụ: `/sim 500k cafe`");
    return;
  }
  
  // Check Income/Expense logic
  var isIncome = content.indexOf("+") !== -1 || 
                 /lương|thưởng|thu|bán|nhận/i.test(description);
  
  // Nếu người dùng không nhập dấu, tự suy luận
  if (amount < 0) {
    isIncome = false; // Đã có dấu -
    amount = Math.abs(amount);
  }
                 
  // Current State
  sendMessage(chatId, "🔮 Đang tính toán tác động của: " + formatMoney(amount) + " (" + description + ")...");
  
  var monthly = getMonthlySummary(); // { totalIncome, totalExpense, netCash }
  var balance = monthly.totalIncome - monthly.totalExpense;
  var currentExpense = monthly.totalExpense;
  
  // Simulation
  var impact = isIncome ? amount : -amount;
  var newBalance = balance + impact;
  
  // Check Goal (Mục tiêu ngày ~587k)
  // Lấy chi tiêu hôm nay
  var daily = getDailySummary();
  var todaySpent = daily.totalExpense;
  var newTodaySpent = todaySpent + (isIncome ? 0 : amount);
  var goalDaily = 587000;
  var goalStatus = newTodaySpent > goalDaily ? "⚠️ Vượt mục tiêu ngày (" + Math.round(newTodaySpent/goalDaily*100) + "%)" : "✅ Trong mục tiêu";
  
  // Check Debt Warning
  var warning = "";
  if (newBalance < 0) warning = "🚫 NGUY HIỂM! Dòng tiền sẽ bị QUYẾT (Âm " + formatMoney(newBalance) + ")";
  else if (newBalance < 2000000) warning = "⚠️ Cảnh báo: Số dư còn lại rất thấp (" + formatMoney(newBalance) + ")";
  
  // Format Message
  var msg = "📊 **KẾT QUẢ MÔ PHỎNG:**\n" +
            "Giao dịch: " + (isIncome ? "🟢 Thu " : "🔴 Chi ") + formatMoney(amount) + "\n" +
            "📝 Nội dung: " + (description || "Không có") + "\n" +
            "━━━━━━━━━━━━━━━━━━━━\n" +
            "💰 **Dòng Tiền (Net Cash):**\n" +
            "• Hiện tại: " + formatMoney(balance) + "\n" +
            "• Sau GD: " + formatMoney(newBalance) + " (" + (impact > 0 ? "📈" : "📉") + ")\n\n" +
            "🎯 **Mục Tiêu Ngày:**\n" +
            "• Đã chi: " + formatMoney(newTodaySpent) + " / " + formatMoney(goalDaily) + "\n" +
            "• Trạng thái: " + goalStatus + "\n";
            
  if (warning) msg += "\n" + warning;
  else msg += "\n✅ Tài chính ổn định. Có thể thực hiện.";
  
  sendMessage(chatId, msg);
}

function parseMoney(str) {
  if (!str) return 0;
  var s = str.toLowerCase().replace(/[+]/g, "").trim();
  var mult = 1;
  
  if (s.indexOf("k") !== -1 || s.indexOf("nghìn") !== -1) mult = 1000;
  else if (s.indexOf("m") !== -1 || s.indexOf("tr") !== -1 || s.indexOf("triệu") !== -1) mult = 1000000;
  else if (s.indexOf("đ") !== -1 || s.indexOf("u") !== -1) mult = 1; // 500000d
  
  var numStr = s.replace(/[^0-9\.,-]/g, ""); // Giữ lại số, dấu . , -
  // Xử lý dấu . và ,
  // Nếu có chuỗi "1.5" => 1.5. Nếu "1,5" => 1.5
  // Nếu "500.000" => 500000
  
  var val = 0;
  // Simple heuristic: Nếu có dấu . và sau đó là 3 số (500.000) -> remove dot
  if (numStr.match(/\.\d{3}$/) || numStr.match(/\.\d{3}\./)) {
    val = parseFloat(numStr.replace(/\./g, "").replace(/,/g, "."));
  } else {
    // 1.5 or 1,5
    val = parseFloat(numStr.replace(/,/g, "."));
  }
  
  if (isNaN(val)) return 0;
  
  // Heuristic: Nếu nhập < 1000 và không có đơn vị, tự nhân 1000 (VD: 500 -> 500k)
  if (val < 1000 && mult === 1 && str.match(/\d$/)) {
     mult = 1000; 
  }
  
  return val * mult;
}

/**
 * Level 8: Báo cáo Vốn & Tồn kho (/von)
 */
function handleCapitalReport(chatId) {
  var props = PropertiesService.getScriptProperties();
  var inv = parseFloat(props.getProperty("INVENTORY_VALUE") || "0");
  
  var monthly = getMonthlySummary();
  var monthlyRevenue = monthly.totalIncome;
  var monthlyCOGS = monthlyRevenue * (1 - BUSINESS.profitMargin); // Giá vốn hàng bán
  
  var monthsOnHand = 0;
  if (monthlyCOGS > 0) {
    monthsOnHand = inv / monthlyCOGS;
  }
  
  var msg = "🏭 **BÁO CÁO VỐN KINH DOANH:**\n" +
            "📦 Giá trị Tồn Kho: " + formatMoney(inv) + "\n" +
            "💰 Doanh thu tháng này: " + formatMoney(monthlyRevenue) + "\n" +
            "🔄 Giá vốn đã bán: " + formatMoney(monthlyCOGS) + "\n" +
            "━━━━━━━━━━━━━━━━━━━━\n";
            
  if (monthsOnHand > 0) {
    msg += "⏳ Tốc độ quay vòng vốn: **" + monthsOnHand.toFixed(1) + " tháng**\n";
    if (monthsOnHand > 3) {
      msg += "⚠️ CẢNH BÁO: Tồn kho quá cao (>3 tháng). Cần đẩy hàng gấp!\n";
    } else if (monthsOnHand < 0.5) {
      msg += "⚡ Tốc độ bán tốt (<2 tuần). Cần nhập thêm hàng?\n";
    } else {
      msg += "✅ Tồn kho ở mức an toàn (1-3 tháng).\n";
    }
  } else {
    msg += "⚠️ Chưa có dữ liệu bán hàng tháng này để tính vòng quay vốn.\n";
  }
  
  msg += "\n💡 *Ghi chú:* Giá trị tồn kho ước tính dựa trên biên lợi nhuận " + (BUSINESS.profitMargin*100) + "%.";
  
  sendMessage(chatId, msg);
}

/**
 * Update Inventory Value manually (/setkho)
 */
function handleSetInventoryCommand(chatId, args) {
  if (args.length === 0) {
    sendMessage(chatId, "📉 Cách dùng:\n1. `/setkho [tổng vốn]` (VD: `/setkho 94tr`)\n2. `/setkho [số lượng] [giá bán TB]` (VD: `/setkho 4733 50k`)");
    return;
  }
  
  var val1 = parseMoney(args[0]);
  var val2 = args.length > 1 ? parseMoney(args[1]) : 0;
  var totalCapital = 0;
  
  if (val2 > 0) {
    // Mode 2: Qty * Price * (1-Margin)
    var qty = val1;
    var price = val2;
    var cost = price * (1 - BUSINESS.profitMargin); // 40% of selling price
    totalCapital = qty * cost;
    sendMessage(chatId, "🧮 Tính toán: " + formatMoney(qty) + " sp x Giá vốn " + formatMoney(cost) + " (Margin " + (BUSINESS.profitMargin*100) + "%)");
  } else {
    // Mode 1: Direct Capital
    totalCapital = val1;
  }
  
  var props = PropertiesService.getScriptProperties();
  props.setProperty("INVENTORY_VALUE", String(totalCapital));
  
  sendMessage(chatId, "✅ Đã cập nhật Vốn Tồn Kho: " + formatMoneyFull(totalCapital));
}
