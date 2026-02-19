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
  
  var payload = {
    "chat_id": chatId,
    "text": text,
    "parse_mode": parseMode || "Markdown"
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
      // Nếu lỗi parse Markdown, thử gửi lại không parse
      if (result.description && result.description.indexOf("parse") > -1) {
        payload.parse_mode = undefined;
        options.payload = JSON.stringify(payload);
        UrlFetchApp.fetch(url, options);
      }
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
  var today = now.getDate();
  var month = now.getMonth() + 1;
  
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
