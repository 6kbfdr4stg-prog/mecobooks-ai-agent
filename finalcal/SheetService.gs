/**
 * ============================================================
 * SHEET SERVICE - Đọc/Ghi dữ liệu Google Sheets
 * ============================================================
 */

/**
 * Lấy Spreadsheet hiện tại
 */
function getSpreadsheet() {
  return SpreadsheetApp.getActiveSpreadsheet();
}

/**
 * Khởi tạo cấu trúc Sheets nếu chưa có
 * Chạy hàm này 1 lần khi setup lần đầu
 */
function initializeSheets() {
  var ss = getSpreadsheet();
  
  // --- Tab Transaction ---
  var txSheet = ss.getSheetByName(SHEET_TRANSACTION);
  if (!txSheet) {
    txSheet = ss.insertSheet(SHEET_TRANSACTION);
    txSheet.appendRow(["Ngày", "Giờ", "Nội dung", "Số tiền", "Loại", "Danh mục"]);
    // Định dạng header
    var headerRange = txSheet.getRange("A1:F1");
    headerRange.setFontWeight("bold");
    headerRange.setBackground("#4285F4");
    headerRange.setFontColor("#FFFFFF");
    // Định dạng cột số tiền
    txSheet.getRange("D:D").setNumberFormat("#,##0");
    txSheet.setColumnWidth(1, 120);
    txSheet.setColumnWidth(2, 80);
    txSheet.setColumnWidth(3, 250);
    txSheet.setColumnWidth(4, 150);
    txSheet.setColumnWidth(5, 80);
    txSheet.setColumnWidth(6, 120);
  }
  
  // --- Tab Dashboard ---
  var dashSheet = ss.getSheetByName(SHEET_DASHBOARD);
  if (!dashSheet) {
    dashSheet = ss.insertSheet(SHEET_DASHBOARD);
    var dashData = [
      ["BẢNG ĐIỀU KHIỂN TÀI CHÍNH", ""],
      ["", ""],
      ["Mục tiêu tích lũy/ngày", BUSINESS.targetDailyAccumulation],
      ["Mục tiêu doanh thu/ngày", BUSINESS.targetDailyRevenue],
      ["Biên lợi nhuận", BUSINESS.profitMargin * 100 + "%"],
      ["Thu nhập thêm/tháng (Share VP)", BUSINESS.monthlyShareOffice],
      ["", ""],
      ["TỔNG NỢ HÀNG THÁNG", TOTAL_MONTHLY_DEBT_PAYMENT],
      ["Tiền nhà (mỗi 3 tháng)", RENT.amount],
      ["Tiền nhà quy đổi/ngày", RENT.dailySaving]
    ];
    dashSheet.getRange(1, 1, dashData.length, 2).setValues(dashData);
    dashSheet.getRange("A1").setFontWeight("bold").setFontSize(14);
    dashSheet.getRange("B:B").setNumberFormat("#,##0");
    dashSheet.setColumnWidth(1, 300);
    dashSheet.setColumnWidth(2, 200);
  }
  
  // --- Tab Debt ---
  var debtSheet = ss.getSheetByName(SHEET_DEBT);
  if (!debtSheet) {
    debtSheet = ss.insertSheet(SHEET_DEBT);
    debtSheet.appendRow(["Tên", "Tên đầy đủ", "Số dư gốc", "Lãi/tháng", "Ngày trả", "Trả hàng tháng", "Loại"]);
    
    DEBTS.forEach(function(debt) {
      debtSheet.appendRow([
        debt.name,
        debt.fullName,
        debt.balance,
        (debt.monthlyRate * 100) + "%",
        debt.payDay || "N/A",
        debt.monthlyPayment,
        debt.type
      ]);
    });
    
    var headerRange = debtSheet.getRange("A1:G1");
    headerRange.setFontWeight("bold");
    headerRange.setBackground("#EA4335");
    headerRange.setFontColor("#FFFFFF");
    debtSheet.getRange("C:C").setNumberFormat("#,##0");
    debtSheet.getRange("F:F").setNumberFormat("#,##0");
  }
  
  Logger.log("✅ Đã khởi tạo 3 tab: Transaction, Dashboard, Debt");
}

/**
 * Ghi một giao dịch vào tab Transaction
 */
function logTransaction(content, amount, type, category) {
  var ss = getSpreadsheet();
  var sheet = ss.getSheetByName(SHEET_TRANSACTION);
  
  if (!sheet) {
    initializeSheets();
    sheet = ss.getSheetByName(SHEET_TRANSACTION);
  }
  
  var now = new Date();
  var dateStr = Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "dd/MM/yyyy");
  var timeStr = Utilities.formatDate(now, "Asia/Ho_Chi_Minh", "HH:mm");
  
  sheet.appendRow([dateStr, timeStr, content, amount, type, category]);
  
  Logger.log("Logged: " + content + " | " + amount + " | " + type);
}

/**
 * Lấy tổng hợp thu/chi trong ngày
 * @param {Date} date - Ngày cần tổng hợp (mặc định: hôm nay)
 * @returns {Object} - {totalIncome, totalExpense, netCash, transactions}
 */
function getDailySummary(date) {
  var ss = getSpreadsheet();
  var sheet = ss.getSheetByName(SHEET_TRANSACTION);
  
  if (!sheet || sheet.getLastRow() <= 1) {
    return { totalIncome: 0, totalExpense: 0, netCash: 0, transactions: [], count: 0 };
  }
  
  var targetDate = date || new Date();
  var targetDateStr = Utilities.formatDate(targetDate, "Asia/Ho_Chi_Minh", "dd/MM/yyyy");
  
  var data = sheet.getRange(2, 1, sheet.getLastRow() - 1, 6).getValues();
  
  var totalIncome = 0;
  var totalExpense = 0;
  var transactions = [];
  
  data.forEach(function(row) {
    var rowDateStr = "";
    if (row[0] instanceof Date) {
      rowDateStr = Utilities.formatDate(row[0], "Asia/Ho_Chi_Minh", "dd/MM/yyyy");
    } else {
      rowDateStr = String(row[0]);
    }
    
    if (rowDateStr === targetDateStr) {
      var amount = Number(row[3]) || 0;
      var type = String(row[4]);
      
      if (type === "Thu") {
        totalIncome += amount;
      } else if (type === "Chi") {
        totalExpense += amount;
      }
      
      transactions.push({
        time: row[1],
        content: row[2],
        amount: amount,
        type: type,
        category: row[5]
      });
    }
  });
  
  return {
    totalIncome: totalIncome,
    totalExpense: totalExpense,
    netCash: totalIncome - totalExpense,
    transactions: transactions,
    count: transactions.length
  };
}

/**
 * Lấy tổng hợp thu/chi trong tháng
 * @returns {Object} - {totalIncome, totalExpense, netCash, daysWithData, avgDailyIncome}
 */
function getMonthlySummary() {
  var ss = getSpreadsheet();
  var sheet = ss.getSheetByName(SHEET_TRANSACTION);
  
  if (!sheet || sheet.getLastRow() <= 1) {
    return { totalIncome: 0, totalExpense: 0, netCash: 0, daysWithData: 0, avgDailyIncome: 0 };
  }
  
  var now = new Date();
  var currentMonth = now.getMonth();
  var currentYear = now.getFullYear();
  
  var data = sheet.getRange(2, 1, sheet.getLastRow() - 1, 6).getValues();
  
  var totalIncome = 0;
  var totalExpense = 0;
  var uniqueDays = {};
  var categoryBreakdown = {};
  
  data.forEach(function(row) {
    var rowDate;
    if (row[0] instanceof Date) {
      rowDate = row[0];
    } else {
      // Parse dd/MM/yyyy
      var parts = String(row[0]).split("/");
      if (parts.length === 3) {
        rowDate = new Date(parseInt(parts[2]), parseInt(parts[1]) - 1, parseInt(parts[0]));
      }
    }
    
    if (rowDate && rowDate.getMonth() === currentMonth && rowDate.getFullYear() === currentYear) {
      var amount = Number(row[3]) || 0;
      var type = String(row[4]);
      var category = String(row[5]);
      var dayKey = Utilities.formatDate(rowDate, "Asia/Ho_Chi_Minh", "dd");
      
      uniqueDays[dayKey] = true;
      
      if (type === "Thu") {
        totalIncome += amount;
      } else if (type === "Chi") {
        totalExpense += amount;
      }
      
      if (!categoryBreakdown[category]) {
        categoryBreakdown[category] = 0;
      }
      categoryBreakdown[category] += amount;
    }
  });
  
  var daysWithData = Object.keys(uniqueDays).length;
  
  return {
    totalIncome: totalIncome,
    totalExpense: totalExpense,
    netCash: totalIncome - totalExpense,
    daysWithData: daysWithData,
    avgDailyIncome: daysWithData > 0 ? Math.round(totalIncome / daysWithData) : 0,
    categoryBreakdown: categoryBreakdown
  };
}

/**
 * Lấy chi tiêu theo danh mục trong tháng
 * @param {string} category - Tên danh mục (VD: "Cafe")
 * @returns {number} - Tổng chi tiêu cho danh mục đó
 */
function getCategorySpending(category) {
  var summary = getMonthlySummary();
  return summary.categoryBreakdown[category] || 0;
}
