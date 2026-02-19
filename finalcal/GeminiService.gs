/**
 * ============================================================
 * GEMINI SERVICE - Gọi Gemini API để phân tích giao dịch
 * ============================================================
 */

/**
 * Gọi Gemini API với prompt
 * @param {string} prompt - Nội dung gửi cho Gemini
 * @param {string} systemInstruction - System prompt (tùy chọn)
 * @returns {string} - Phản hồi từ Gemini
 */
function callGemini(prompt, systemInstruction, modelName) {
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

  // Use Pro model for smarter answers
  var response = callGemini(question, systemPrompt, GEMINI_MODEL_SMART);
  return response || "Xin lỗi, tôi không thể trả lời câu hỏi này lúc này.";
}
