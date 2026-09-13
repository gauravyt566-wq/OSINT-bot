<?php
error_reporting(E_ALL);
ini_set('display_errors', 0);

$BOT_TOKEN = "8688224146:AAFDT2xBblVpRS-nXYzvDOv6D6DglorA6gE";
$BOT_USERNAME = "@CyberWalaBandaBot";
$ADMIN_IDS = ["7255220723"];

$FORCE_CHANNELS = [
    "@PrivateLimitedHub",
    "@CyberWalaBandaGC"
];

$PRIVATE_BOT_LINK = "https://t.me/CyberWalaBandaBot";
$GROUP_ADD_LINK = "https://t.me/CyberWalaBandaBot?startgroup=true";

$API_ENDPOINTS = [
    'mobile'    => "https://ansh-apis.is-dev.org/api/new?key=ansh&num={term}",
    'aadhaar'   => "https://number-info-woad-five.vercel.app/search?q={term}",
    'family'    => "https://family-three-azure.vercel.app/?aadhar={term}",
    'ration'    => "https://new-ration-three.vercel.app/?ration={term}",
    'lpg'       => "https://lpg-pied.vercel.app/umang_lpg?num={term}",
    'ifsc'      => "https://ifsc.razorpay.com/{term}",
    'ip'        => "https://ip-info-smoky.vercel.app/lookup?ip={term}",
    'telegram'  => "https://darkxosint.site/?type=tg_numb&key=zephrex&query={term}",
    'paytm'     => "https://paytm-to-num-one.vercel.app/fetch?upi={term}",
    'pincode'   => "https://pincode-ng.vercel.app/lookup?pincode={term}",
    'freefire'  => "https://ff.gauravyt342.workers.dev/?uid={term}",
    'vehicle'   => "https://paytm-to-num-zzpd.vercel.app/?chu={term}",
    'mob2veh'   => "https://num-vnum-eta.vercel.app/api/vehicle?mobile={term}",
    'challan'   => "https://challan-api-sepia.vercel.app/api/vehicle?number={term}",
    'instagram' => "https://insta-profile-info-api.vercel.app/api/instagram.php?username={term}",
    'vnum'      => "https://parivahan-teal.vercel.app/fetch?vehicle_number={term}",
    'pangst'    => "https://pan-2-gst-sable.vercel.app/api?pan={term}",
    'gst'       => "https://gst.gauravyt492.workers.dev/?gst={term}",
    'pan'       => "https://pan-api-two.vercel.app/?pan={term}",
    'chassis'   => "https://chassis-engine-lookup-rosy.vercel.app/chassis?number={term}",
    'engine'    => "https://chassis-engine-lookup-rosy.vercel.app/engine?number={term}"
];

$RESULT_TITLES = [
    'mobile'    => "📲 Mobile Info Result",
    'aadhaar'   => "🪪 Aadhaar Info Result",
    'family'    => "👨‍👩‍👧‍👦 Family Info Result",
    'ration'    => "🍚 Ration Card Result",
    'lpg'       => "🛢️ LPG Info Result",
    'ifsc'      => "🏦 IFSC Info Result",
    'ip'        => "🌐 IP Lookup Result",
    'telegram'  => "✈️ Telegram Info Result",
    'paytm'     => "💳 Paytm Info Result",
    'pincode'   => "📍 Pincode Info Result",
    'freefire'  => "🎮 Free Fire Info Result",
    'vehicle'   => "🏍 Vehicle RC Result",
    'mob2veh'   => "📱→🚗 Mobile to Vehicle Result",
    'challan'   => "🚔 Challan Info Result",
    'instagram' => "📸 Instagram Info Result",
    'vnum'      => "🚗 Vehicle to Number Result",
    'pangst'    => "📇 PAN to GST Result",
    'gst'       => "🏢 GST Info Result",
    'pan'       => "💳 PAN Info Result",
    'chassis'   => "🔩 Chassis Info Result",
    'engine'    => "⚙️ Engine Info Result"
];

function isAdmin($userId) {
    return in_array((string)$userId, $GLOBALS['ADMIN_IDS']);
}

function checkForceJoin($userId) {
    global $BOT_TOKEN, $FORCE_CHANNELS;
    if (empty($FORCE_CHANNELS)) return true;
    foreach ($FORCE_CHANNELS as $chat) {
        $url = "https://api.telegram.org/bot$BOT_TOKEN/getChatMember?chat_id=" . urlencode($chat) . "&user_id=" . $userId;
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 10);
        curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
        $response = curl_exec($ch);
        curl_close($ch);
        if ($response === false) return false;
        $data = json_decode($response, true);
        $status = $data['result']['status'] ?? '';
        if (!in_array($status, ['member', 'administrator', 'creator'])) {
            return false;
        }
    }
    return true;
}

function getForceJoinKeyboard() {
    global $FORCE_CHANNELS;
    $buttons = [];
    $channelCount = 1;
    foreach ($FORCE_CHANNELS as $channel) {
        $clean = ltrim($channel, '@');
        $buttons[] = [[
            'text' => "📢 JOIN CHANNEL " . $channelCount,
            'url' => "https://t.me/" . $clean
        ]];
        $channelCount++;
    }
    $buttons[] = [['text' => '✅ CHECK JOIN', 'callback_data' => 'check_join']];
    return ['inline_keyboard' => $buttons];
}

function sendForceJoinMessage($chatId, $replyTo = null) {
    global $FORCE_CHANNELS;
    $channelList = "";
    foreach ($FORCE_CHANNELS as $c) {
        $channelList .= "• " . $c . "\n";
    }
    $msg = "🔒 <b>PLEASE JOIN OUR CHANNEL(S) TO USE THIS BOT</b>\n━━━━━━━━━━━━━━━━━━\n\n";
    $msg .= $channelList . "\n";
    $msg .= "✅ No Referral System\n";
    $msg .= "✅ No Limits\n";
    $msg .= "✅ Fast & Reliable Updates\n\n";
    $msg .= "👇 Join Now & Stay Connected!";
    sendMessage($chatId, $msg, getForceJoinKeyboard(), $replyTo);
}

function fetchApi($url) {
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 20);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 8);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
    curl_setopt($ch, CURLOPT_USERAGENT, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36');
    $response = curl_exec($ch);
    curl_close($ch);
    if ($response === false) return null;
    return $response;
}

function safeParseContent($content) {
    if (is_array($content)) return $content;
    if (!is_string($content)) return null;
    $decoded = json_decode($content, true);
    if ($decoded !== null) return $decoded;
    $start = strpos($content, "{");
    $end = strrpos($content, "}");
    if ($start !== false && $end !== false && $end > $start) {
        $cleanStr = substr($content, $start, $end - $start + 1);
        $decoded = json_decode($cleanStr, true);
        if ($decoded !== null) return $decoded;
    }
    return null;
}

function sendMessage($chatId, $text, $replyMarkup = null, $replyTo = null) {
    global $BOT_TOKEN;
    $postData = ['chat_id' => $chatId, 'text' => $text, 'parse_mode' => 'HTML'];
    if ($replyMarkup) $postData['reply_markup'] = json_encode($replyMarkup);
    if ($replyTo) $postData['reply_to_message_id'] = $replyTo;
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, "https://api.telegram.org/bot$BOT_TOKEN/sendMessage");
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $postData);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 10);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    $response = curl_exec($ch);
    curl_close($ch);
    return json_decode($response, true);
}

function editMessageText($chatId, $messageId, $text) {
    global $BOT_TOKEN;
    $postData = ['chat_id' => $chatId, 'message_id' => $messageId, 'text' => $text, 'parse_mode' => 'HTML'];
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, "https://api.telegram.org/bot$BOT_TOKEN/editMessageText");
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $postData);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 10);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    $response = curl_exec($ch);
    curl_close($ch);
    return json_decode($response, true);
}

function deleteMessage($chatId, $messageId) {
    global $BOT_TOKEN;
    $postData = ['chat_id' => $chatId, 'message_id' => $messageId];
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, "https://api.telegram.org/bot$BOT_TOKEN/deleteMessage");
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $postData);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 10);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    $response = curl_exec($ch);
    curl_close($ch);
    return json_decode($response, true);
}

function answerCallbackQuery($callbackQueryId, $text = '', $showAlert = false) {
    global $BOT_TOKEN;
    $postData = ['callback_query_id' => $callbackQueryId, 'text' => $text, 'show_alert' => $showAlert];
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, "https://api.telegram.org/bot$BOT_TOKEN/answerCallbackQuery");
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $postData);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 5);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 3);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    $response = curl_exec($ch);
    curl_close($ch);
    return json_decode($response, true);
}

function scheduleDelete($chatId, $messageId) {
    $time = time() + 60;
    $file = sys_get_temp_dir() . '/bot_delete_queue.json';
    $queue = [];
    if (file_exists($file)) {
        $queue = json_decode(file_get_contents($file), true) ?: [];
    }
    $queue[] = ['chat_id' => $chatId, 'message_id' => $messageId, 'time' => $time];
    file_put_contents($file, json_encode($queue));
}

function processPendingDeletes() {
    $file = sys_get_temp_dir() . '/bot_delete_queue.json';
    if (!file_exists($file)) return;
    $queue = json_decode(file_get_contents($file), true) ?: [];
    $now = time();
    $remaining = [];
    foreach ($queue as $item) {
        if ($item['time'] <= $now) {
            editMessageText($item['chat_id'], $item['message_id'], "🗑️ Message Deleted Successfully");
        } else {
            $remaining[] = $item;
        }
    }
    file_put_contents($file, json_encode($remaining));
}

function processLookupRequest($chatId, $userId, $lookupType, $term, $replyTo = null) {
    global $API_ENDPOINTS, $RESULT_TITLES;

    if (!checkForceJoin($userId)) {
        sendForceJoinMessage($chatId, $replyTo);
        return;
    }

    $apiEndpoint = $API_ENDPOINTS[$lookupType] ?? null;
    if (!$apiEndpoint) {
        sendMessage($chatId, "❌ Invalid lookup type.", null, $replyTo);
        return;
    }

    $apiUrl = str_replace('{term}', urlencode($term), $apiEndpoint);

    $statusMsg = sendMessage($chatId, "⏳ Processing your request...", null, $replyTo);
    $statusMessageId = $statusMsg['result']['message_id'] ?? null;

    $rawContent = fetchApi($apiUrl);

    if ($statusMessageId) {
        deleteMessage($chatId, $statusMessageId);
    }

    if ($rawContent === null) {
        sendMessage($chatId, "❌ <b>API ERROR</b>\n\nAPI se koi response nahi mila.", null, $replyTo);
        return;
    }

    $parsed = safeParseContent($rawContent);

    if (!$parsed) {
        $debugText = "⚠️ <b>Error: API response is not valid JSON.</b>\n\n<b>DEBUG OUTPUT:</b>\n\n<pre>" . htmlspecialchars(substr($rawContent, 0, 3000), ENT_QUOTES, 'UTF-8') . "</pre>";
        sendMessage($chatId, $debugText, null, $replyTo);
        return;
    }

    $prettyJson = json_encode($parsed, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);

    $maxLen = 3500;
    if (strlen($prettyJson) > $maxLen) {
        $prettyJson = substr($prettyJson, 0, $maxLen) . "\n\n... Result too long, trimmed.";
    }

    $title = $RESULT_TITLES[$lookupType] ?? "📋 Result";
    $msg = $title . ":\n\n<pre>" . htmlspecialchars($prettyJson, ENT_QUOTES, 'UTF-8') . "</pre>";

    $keyboard = ['inline_keyboard' => [
        [['text' => '🤫 Use Privately', 'url' => $GLOBALS['PRIVATE_BOT_LINK']]],
        [['text' => '➕ Add me to Your Group', 'url' => $GLOBALS['GROUP_ADD_LINK']]]
    ]];

    $sent = sendMessage($chatId, $msg, $keyboard, $replyTo);
    $sentId = $sent['result']['message_id'] ?? null;

    if ($sentId) {
        scheduleDelete($chatId, $sentId);
    }
}

function getWelcomeKeyboard() {
    global $PRIVATE_BOT_LINK, $GROUP_ADD_LINK;
    return ['inline_keyboard' => [
        [['text' => '🤫 Use Privately', 'url' => $PRIVATE_BOT_LINK]],
        [['text' => '➕ Add me to Your Group', 'url' => $GROUP_ADD_LINK]]
    ]];
}

function handleStart($chatId, $userId, $name, $username, $replyTo = null) {
    if (!checkForceJoin($userId)) {
        sendForceJoinMessage($chatId, $replyTo);
        return;
    }

    $welcome = "🎉 <b>Welcome! You can now use me:</b>\n\nUse /help to see all available commands.";
    sendMessage($chatId, $welcome, getWelcomeKeyboard(), $replyTo);
}

function handleHelp($chatId, $userId, $replyTo = null) {
    $helpMsg = "⚡️ <b>Available Commands</b>\n\n";
    $helpMsg .= "⚡️ <code>/num</code> - NUMBER TO DETAILS\n";
    $helpMsg .= "⚡️ <code>/aadhar</code> - AADHAR TO INFO\n";
    $helpMsg .= "⚡️ <code>/tg</code> - TELEGRAM UID TO NUMBER\n";
    $helpMsg .= "⚡️ <code>/rc</code> - RC DETAILS\n";
    $helpMsg .= "⚡️ <code>/vehicle</code> - VEHICLE DETAILS\n";
    $helpMsg .= "⚡️ <code>/family</code> - FAMILY DETAILS\n";
    $helpMsg .= "⚡️ <code>/vnum</code> - VEHICLE TO OWNER NUM\n";
    $helpMsg .= "⚡️ <code>/lpg</code> - LPG INFO\n";
    $helpMsg .= "⚡️ <code>/challan</code> - CHALLAN INFO\n";
    $helpMsg .= "⚡️ <code>/chassis</code> - CHASSIS INFO\n";
    $helpMsg .= "⚡️ <code>/engine</code> - ENGINE INFO\n";
    $helpMsg .= "⚡️ <code>/insta</code> - INSTAGRAM INFO\n";
    $helpMsg .= "⚡️ <code>/pan</code> - PAN INFO\n";
    $helpMsg .= "⚡️ <code>/gst</code> - GST INFO\n";
    $helpMsg .= "⚡️ <code>/pangst</code> - PAN TO GST INFO\n";
    $helpMsg .= "⚡️ <code>/ip</code> - IP ADDRESS LOOKUP\n";
    $helpMsg .= "⚡️ <code>/pincode</code> - PINCODE INFO\n";
    $helpMsg .= "⚡️ <code>/ifsc</code> - IFSC CODE INFO\n";
    $helpMsg .= "⚡️ <code>/ff</code> - FREE FIRE UID INFO\n";
    $helpMsg .= "⚡️ <code>/paytm</code> - PAYTM UPI INFO\n";
    $helpMsg .= "⚡️ <code>/ration</code> - RATION CARD INFO\n";
    $helpMsg .= "⚡️ <code>/mob2veh</code> - MOBILE TO VEHICLE NUM";

    sendMessage($chatId, $helpMsg, null, $replyTo);
}

function handleCallback($callbackQuery) {
    $callbackId = $callbackQuery['id'];
    $userId = $callbackQuery['from']['id'];
    $chatId = $callbackQuery['message']['chat']['id'];
    $messageId = $callbackQuery['message']['message_id'];
    $data = $callbackQuery['data'];

    if ($data === 'check_join') {
        if (checkForceJoin($userId)) {
            answerCallbackQuery($callbackId, '✅ Thanks for joining!');
            deleteMessage($chatId, $messageId);
            $welcome = "🎉 <b>Welcome! You can now use me:</b>\n\nUse /help to see all available commands.";
            sendMessage($chatId, $welcome, getWelcomeKeyboard());
        } else {
            answerCallbackQuery($callbackId, '❌ Please join all channels first!', true);
        }
        return;
    }

    answerCallbackQuery($callbackId);
}

function handleCommand($message) {
    $chatId = $message['chat']['id'];
    $userId = $message['from']['id'];
    $name = $message['from']['first_name'] ?? 'User';
    $username = $message['from']['username'] ?? 'No Username';
    $text = $message['text'] ?? '';
    $messageId = $message['message_id'] ?? null;

    $parts = explode(' ', $text);
    $command = strtolower($parts[0]);
    if (strpos($command, '@') !== false) {
        $command = explode('@', $command)[0];
    }
    $args = array_slice($parts, 1);

    switch ($command) {
        case '/start':
            handleStart($chatId, $userId, $name, $username, $messageId);
            break;
        case '/help':
            if (!checkForceJoin($userId)) {
                sendForceJoinMessage($chatId, $messageId);
                return;
            }
            handleHelp($chatId, $userId, $messageId);
            break;
        case '/num':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/num 9876543210</code>", null, $messageId); return; }
            processLookupRequest($chatId, $userId, 'mobile', $args[0], $messageId);
            break;
        case '/aadhar':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/aadhar 123456789012</code>", null, $messageId); return; }
            processLookupRequest($chatId, $userId, 'aadhaar', $args[0], $messageId);
            break;
        case '/family':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/family 123456789012</code>", null, $messageId); return; }
            processLookupRequest($chatId, $userId, 'family', $args[0], $messageId);
            break;
        case '/ration':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/ration 123456789012</code>", null, $messageId); return; }
            processLookupRequest($chatId, $userId, 'ration', $args[0], $messageId);
            break;
        case '/lpg':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/lpg 1234567890</code>", null, $messageId); return; }
            processLookupRequest($chatId, $userId, 'lpg', $args[0], $messageId);
            break;
        case '/paytm':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/paytm example@ptyes</code>", null, $messageId); return; }
            processLookupRequest($chatId, $userId, 'paytm', $args[0], $messageId);
            break;
        case '/pan':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/pan ABCDE1234F</code>", null, $messageId); return; }
            processLookupRequest($chatId, $userId, 'pan', $args[0], $messageId);
            break;
        case '/gst':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/gst 22AAAAA0000A1Z5</code>", null, $messageId); return; }
            processLookupRequest($chatId, $userId, 'gst', $args[0], $messageId);
            break;
        case '/pangst':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/pangst ABCDE1234F</code>", null, $messageId); return; }
            processLookupRequest($chatId, $userId, 'pangst', $args[0], $messageId);
            break;
        case '/vehicle':
        case '/rc':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/vehicle MH01AB1234</code>", null, $messageId); return; }
            processLookupRequest($chatId, $userId, 'vehicle', $args[0], $messageId);
            break;
        case '/vnum':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/vnum MH01AB1234</code>", null, $messageId); return; }
            processLookupRequest($chatId, $userId, 'vnum', $args[0], $messageId);
            break;
        case '/mob2veh':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/mob2veh 9876543210</code>", null, $messageId); return; }
            processLookupRequest($chatId, $userId, 'mob2veh', $args[0], $messageId);
            break;
        case '/challan':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/challan MH01AB1234</code>", null, $messageId); return; }
            processLookupRequest($chatId, $userId, 'challan', $args[0], $messageId);
            break;
        case '/chassis':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/chassis ABC1234567890</code>", null, $messageId); return; }
            processLookupRequest($chatId, $userId, 'chassis', $args[0], $messageId);
            break;
        case '/engine':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/engine ABC1234567890</code>", null, $messageId); return; }
            processLookupRequest($chatId, $userId, 'engine', $args[0], $messageId);
            break;
        case '/ip':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/ip 192.168.1.1</code>", null, $messageId); return; }
            processLookupRequest($chatId, $userId, 'ip', $args[0], $messageId);
            break;
        case '/pincode':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/pincode 400001</code>", null, $messageId); return; }
            processLookupRequest($chatId, $userId, 'pincode', $args[0], $messageId);
            break;
        case '/tg':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/tg 9876543210</code>", null, $messageId); return; }
            processLookupRequest($chatId, $userId, 'telegram', $args[0], $messageId);
            break;
        case '/insta':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/insta username</code>", null, $messageId); return; }
            processLookupRequest($chatId, $userId, 'instagram', $args[0], $messageId);
            break;
        case '/ifsc':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/ifsc SBIN0001234</code>", null, $messageId); return; }
            processLookupRequest($chatId, $userId, 'ifsc', $args[0], $messageId);
            break;
        case '/ff':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/ff 1234567890</code>", null, $messageId); return; }
            processLookupRequest($chatId, $userId, 'freefire', $args[0], $messageId);
            break;
        default:
            if (strpos($text, '/') === 0) {
                if (!checkForceJoin($userId)) {
                    sendForceJoinMessage($chatId, $messageId);
                    return;
                }
                sendMessage($chatId, "❓ Unknown command. Use /help to see available commands.", null, $messageId);
            }
            break;
    }
}

processPendingDeletes();

$input = file_get_contents('php://input');
$update = json_decode($input, true);

if (isset($update['message'])) {
    handleCommand($update['message']);
} elseif (isset($update['callback_query'])) {
    handleCallback($update['callback_query']);
}

header('Content-Type: application/json');
echo json_encode(['ok' => true]);
?>
