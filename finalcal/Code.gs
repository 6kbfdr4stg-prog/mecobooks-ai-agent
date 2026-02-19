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
function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    
    if (!data.message || !data.message.text) {
      return ContentService.createTextOutput("OK");
    }
    
    var chatId = data.message.chat.id;
    var userText = data.message.text.trim();
    
    // Xử lý lệnh (bắt đầu bằng /)
    if (userText.startsWith("/")) {
      handleCommand(chatId, userText);
    } else {
      processMessage(chatId, userText);
    }
    
  } catch (error) {
    Logger.log("doPost error: " + error.toString());
  }
  
  return ContentService.createTextOutput("OK");
}

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
  var cmd = command.toLowerCase().split(" ")[0];
  
  switch (cmd) {
    case "/start":
    case "/help":
      sendHelp(chatId);
      break;
      
    case "/baocao":
    case "/bc":
      sendDailyReport(chatId);
      break;
      
    case "/thang":
    case "/month":
      sendMonthlyReport(chatId);
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
  lines.push("/thang - Báo cáo tháng");
  lines.push("/no - Bảng tổng hợp nợ");
  lines.push("/nha - Tiến độ tiền nhà");
  lines.push("/mt - Mục tiêu & KPI");
  lines.push("/risk - Kiểm tra rủi ro dòng tiền");
  lines.push("/tuvan - Xin lời khuyên AI");
  lines.push("/help - Danh sách lệnh");
  lines.push("");
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
    lines.push("💸 Chi: -" + formatMoneyFull(daily.totalExpense));
    lines.push("📈 Ròng: " + formatMoneyFull(daily.netCash));
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
  var now = new Date();
  var monthName = "Tháng " + (now.getMonth() + 1) + "/" + now.getFullYear();
  
  var monthlyProfit = monthly.totalIncome * BUSINESS.profitMargin;
  var targetMonthlyRevenue = BUSINESS.targetDailyRevenue * 30;
  var revenueProgress = monthly.totalIncome > 0 ? Math.round((monthly.totalIncome / targetMonthlyRevenue) * 100) : 0;
  
  var lines = [];
  lines.push("📅 *BÁO CÁO " + monthName + "*");
  lines.push("━━━━━━━━━━━━━━━━━━━━");
  lines.push("");
  lines.push("💰 Tổng doanh thu: " + formatMoneyFull(monthly.totalIncome));
  lines.push("💸 Tổng chi: " + formatMoneyFull(monthly.totalExpense));
  lines.push("📈 Ròng: " + formatMoneyFull(monthly.netCash));
  lines.push("📊 Lợi nhuận (60%): " + formatMoneyFull(monthlyProfit));
  lines.push("");
  lines.push("📈 TB doanh thu/ngày: " + formatMoney(monthly.avgDailyIncome));
  lines.push("📆 Số ngày có dữ liệu: " + monthly.daysWithData);
  lines.push("🎯 Tiến độ DT tháng: " + revenueProgress + "%");
  
  // Chi tiết theo danh mục
  if (monthly.categoryBreakdown && Object.keys(monthly.categoryBreakdown).length > 0) {
    lines.push("");
    lines.push("🏷 *Theo danh mục:*");
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
  sendMessage(chatId, "💡 *LỜI KHUYÊN TÀI CHÍNH*\n━━━━━━━━━━━━━━━━━━━━\n\n" + advice);
}

/**
 * Hàm test - Gọi thủ công để kiểm tra
 */
function testBot() {
  // Test gửi tin nhắn
  sendMessage(OWNER_CHAT_ID, "🤖 Bot đang hoạt động! Gõ /help để bắt đầu.");
  Logger.log("✅ Test thành công!");
}

/**
 * Thiết lập webhook cho Telegram
 * Chạy hàm này 1 lần sau khi deploy webapp
 * @param {string} webhookUrl - URL webapp từ Apps Script
 */
function setWebhook(webhookUrl) {
  if (!webhookUrl) {
    Logger.log("❌ Vui lòng truyền URL webhook. Ví dụ: setWebhookManual()");
    return;
  }
  
  var url = "https://api.telegram.org/bot" + TELEGRAM_TOKEN + "/setWebhook?url=" + encodeURIComponent(webhookUrl);
  var response = UrlFetchApp.fetch(url);
  Logger.log("Webhook result: " + response.getContentText());
}

/**
 * Thiết lập webhook thủ công
 * Thay URL_WEBAPP bằng URL webapp thực tế của bạn
 */
function setWebhookManual() {
  var webappUrl = "DÁN_URL_WEBAPP_VÀO_ĐÂY"; // Thay đổi URL này
  setWebhook(webappUrl);
}
