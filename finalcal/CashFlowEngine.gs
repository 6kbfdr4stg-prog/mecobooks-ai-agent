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
  var today = now.getDate();
  var daysInMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate();
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
  
  lines.push("📊 *BẢNG TỔNG HỢP NỢ*");
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
      var today = now.getDate();
      var daysLeft = debt.payDay > today ? debt.payDay - today : debt.payDay + 30 - today;
      status = " (còn " + daysLeft + " ngày)";
    }
    
    lines.push("");
    lines.push(icon + " *" + debt.fullName + "*" + status);
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
  lines.push("💰 Tổng nợ: *" + formatMoney(totalDebt) + "*");
  lines.push("💸 Tổng lãi/tháng: *" + formatMoney(totalMonthlyInterest) + "*");
  lines.push("📅 Tổng trả/tháng: *" + formatMoney(totalMonthlyPayment) + "*");
  
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
