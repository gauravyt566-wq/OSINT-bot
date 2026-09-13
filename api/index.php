<?php
error_reporting(E_ALL);
ini_set('display_errors', 0);

$BOT_TOKEN = "8688224146:AAFDT2xBblVpRS-nXYzvDOv6D6DglorA6gE";
$BOT_USERNAME = "@CyberWalaBandaBot";
$ADMIN_IDS = ["7255220723"];

$FORCE_CHANNEL = "@CyberWalaBandaGC";
$FORCE_CHANNEL_LINK = "https://t.me/CyberWalaBandaGC";
$FORCE_GROUP = "@CyberWalaBandaGC";
$FORCE_GROUP_LINK = "https://t.me/CyberWalaBandaGC";
$SECRET_GROUP_LINK = "https://t.me/CyberWalaBandaGC";

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

function isAdmin($userId) {
    return in_array((string)$userId, $GLOBALS['ADMIN_IDS']);
}

function checkForceJoin($userId) {
    global $BOT_TOKEN, $FORCE_CHANNEL, $FORCE_GROUP;
    $chats = [];
    if ($FORCE_CHANNEL) $chats[] = $FORCE_CHANNEL;
    if ($FORCE_GROUP && $FORCE_GROUP !== $FORCE_CHANNEL) $chats[] = $FORCE_GROUP;
    if (empty($chats)) return true;

    foreach ($chats as $chat) {
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
    global $FORCE_CHANNEL_LINK, $FORCE_GROUP_LINK;
    $rows = [];
    if ($FORCE_CHANNEL_LINK) $rows[] = [['text' => '📢 JOIN CHANNEL', 'url' => $FORCE_CHANNEL_LINK]];
    if ($FORCE_GROUP_LINK) $rows[] = [['text' => '💬 JOIN GROUP', 'url' => $FORCE_GROUP_LINK]];
    $rows[] = [['text' => '✅ CHECK JOIN', 'callback_data' => 'check_join']];
    return ['inline_keyboard' => $rows];
}

function sendForceJoinMessage($chatId) {
    $msg = "🔒 <b>PLEASE JOIN OUR CHANNEL & GROUP TO USE THIS BOT</b>\n━━━━━━━━━━━━━━━━━━\n\n";
    $msg .= "✅ No Referral System\n";
    $msg .= "✅ No Limits\n";
    $msg .= "✅ Fast & Reliable Updates\n\n";
    $msg .= "Join now and stay connected. 🚬\n\n";
    $msg .= "TG TO NUMBER ALSO AVAILABLE FREE\n";
    $msg .= "VEHICLE TO NUM ALSO AVAILABLE FREE\n\n";
    $msg .= "Unlimited use no any limit\n\n";
    $msg .= "👇 Join Here: " . $GLOBALS['FORCE_CHANNEL_LINK'];
    sendMessage($chatId, $msg, getForceJoinKeyboard());
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
    $decoded = json_decode($response, true);
    return $decoded !== null ? $decoded : $response;
}

function sendMessage($chatId, $text, $replyMarkup = null) {
    global $BOT_TOKEN;
    $postData = ['chat_id' => $chatId, 'text' => $text, 'parse_mode' => 'HTML'];
    if ($replyMarkup) $postData['reply_markup'] = json_encode($replyMarkup);
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

function splitResultParts($text, $maxLen = 3500) {
    if (strlen($text) <= $maxLen) return [$text];
    $parts = [];
    $remaining = $text;
    while (strlen($remaining) > $maxLen) {
        $cut = strrpos(substr($remaining, 0, $maxLen), "\n");
        if ($cut === false || $cut < ($maxLen / 2)) $cut = $maxLen;
        $parts[] = substr($remaining, 0, $cut);
        $remaining = substr($remaining, $cut);
    }
    if (trim($remaining) !== '') $parts[] = $remaining;
    return $parts;
}

function sendResultParts($chatId, $text) {
    $parts = splitResultParts($text, 3500);
    $total = count($parts);
    $lastMsg = null;
    foreach ($parts as $i => $part) {
        $num = $i + 1;
        $header = "\n\n━━━━━━━━━━━━━━━━━━━━━━━\n📄 <b>PART $num / $total</b>\n━━━━━━━━━━━━━━━━━━━━━━━";
        $lastMsg = sendMessage($chatId, $part . $header);
        usleep(150000);
    }
    return $lastMsg;
}

function processLookupRequest($chatId, $userId, $lookupType, $term, $isGroup = false) {
    global $API_ENDPOINTS;

    if (!checkForceJoin($userId)) {
        sendForceJoinMessage($chatId);
        return;
    }

    $apiEndpoint = $API_ENDPOINTS[$lookupType] ?? null;
    if (!$apiEndpoint) {
        sendMessage($chatId, "❌ Invalid lookup type.");
        return;
    }

    $apiUrl = str_replace('{term}', urlencode($term), $apiEndpoint);

    $statusMsg = sendMessage($chatId, "⏳ Processing your request...");
    $statusMessageId = $statusMsg['result']['message_id'] ?? null;

    $rawData = fetchApi($apiUrl);

    if ($statusMessageId) {
        deleteMessage($chatId, $statusMessageId);
    }

    if ($rawData === null) {
        sendMessage($chatId, "❌ <b>API ERROR</b>\n\nAPI se koi response nahi mila.");
        return;
    }

    if (is_array($rawData)) {
        if (isset($rawData['data']) && is_array($rawData['data'])) {
            $rawData['data']['_powered_by'] = "@CyberWalaBanda";
        } else {
            $rawData['_powered_by'] = "@CyberWalaBanda";
        }
        $jsonText = json_encode($rawData, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    } else {
        $jsonText = (string)$rawData . "\n\n_powered_by: @CyberWalaBanda";
    }

    $header = "📋 <b>API RESPONSE (JSON)</b>\n━━━━━━━━━━━━━━━━━━━━━━━\n";
    $footer = "\n━━━━━━━━━━━━━━━━━━━━━━━";

    $formatted = $header . "<pre>" . htmlspecialchars($jsonText, ENT_QUOTES, 'UTF-8') . "</pre>" . $footer;

    sendResultParts($chatId, $formatted);
}

function getWelcomeKeyboard() {
    global $BOT_USERNAME;
    return ['inline_keyboard' => [
        [['text' => '➕ ADD ME TO YOUR GROUP', 'url' => "https://t.me/" . ltrim($BOT_USERNAME, '@') . "?startgroup=true"]],
        [['text' => '🕵️ USE ME SECRETLY', 'url' => $GLOBALS['SECRET_GROUP_LINK']]]
    ]];
}

function handleStart($chatId, $userId, $name, $username, $isGroup = false) {
    if (!checkForceJoin($userId)) {
        sendForceJoinMessage($chatId);
        return;
    }

    $welcome = "🎉 <b>Welcome! You can now use me:</b>\n\nUse /help to see all available commands.";
    sendMessage($chatId, $welcome, getWelcomeKeyboard());
}

function handleHelp($chatId, $userId, $name) {
    $helpMsg = "⚡️ <b>Available Commands</b>\n\n";
    $helpMsg .= "⚡️ /num - NUMBER TO DETAILS\n";
    $helpMsg .= "⚡️ /aadhar - AADHAR TO INFO\n";
    $helpMsg .= "⚡️ /tg - TELEGRAM UID TO NUMBER\n";
    $helpMsg .= "⚡️ /rc - RC DETAILS\n";
    $helpMsg .= "⚡️ /vehicle - VEHICLE NUMBER TO OWNER ADDRESS\n";
    $helpMsg .= "⚡️ /family - AADHAR NUMBER TO FAMILY DETAILS\n";
    $helpMsg .= "⚡️ /email - EMAIL TO INFO\n";
    $helpMsg .= "⚡️ /vnum - VEHICLE TO OWNER NUM\n";
    $helpMsg .= "⚡️ /leak - ADV OSINT SEARCH\n";
    $helpMsg .= "⚡️ /lpg - LPG GAS INFO USING MOBILE NUMBER\n";
    $helpMsg .= "⚡️ /mp - MP MOBILE NUM TO PIC + FAMILY INFO\n";
    $helpMsg .= "⚡️ /challan - Challan info + challan pdf\n";
    $helpMsg .= "⚡️ /hp - HP - LPG PIPELINE INFO THROUGH NUM\n";
    $helpMsg .= "⚡️ /chassis - GET VEHICLE INFO FROM CHASSIS NUM\n";
    $helpMsg .= "⚡️ /eng - GET VEHICLE INFO FROM ENGINE NUMBER\n";
    $helpMsg .= "⚡️ /ig - INSTA ID TO BASIC DETAILS\n";
    $helpMsg .= "⚡️ /pvtig - PVT INSTA ID FOLLOWER LOOKUP\n";
    $helpMsg .= "⚡️ /pan - PAN INFO";
    $keyboard = ['inline_keyboard' => [
        [['text' => '📞 CONTACT SUPPORT', 'url' => 'https://t.me/CyberWalaBanda']]
    ]];
    sendMessage($chatId, $helpMsg, $keyboard);
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
            answerCallbackQuery($callbackId, '❌ Please join channel & group first!', true);
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
    $chatType = $message['chat']['type'] ?? 'private';
    $isGroup = in_array($chatType, ['group', 'supergroup']);

    $parts = explode(' ', $text);
    $command = strtolower($parts[0]);
    if (strpos($command, '@') !== false) {
        $command = explode('@', $command)[0];
    }
    $args = array_slice($parts, 1);

    $forceJoinCommands = ['/start', '/help', '/num', '/aadhar', '/family', '/ration', '/lpg', '/paytm', '/pan', '/gst', '/pangst', '/vehicle', '/vnum', '/mob2veh', '/challan', '/chassis', '/engine', '/ip', '/pincode', '/tg', '/insta', '/ifsc', '/ff'];

    if (in_array($command, $forceJoinCommands)) {
        if (!checkForceJoin($userId)) {
            sendForceJoinMessage($chatId);
            return;
        }
    }

    switch ($command) {
        case '/start':
            handleStart($chatId, $userId, $name, $username, $isGroup);
            break;
        case '/help':
            handleHelp($chatId, $userId, $name);
            break;
        case '/num':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/num 9876543210</code>"); return; }
            processLookupRequest($chatId, $userId, 'mobile', $args[0], $isGroup);
            break;
        case '/aadhar':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/aadhar 123456789012</code>"); return; }
            processLookupRequest($chatId, $userId, 'aadhaar', $args[0], $isGroup);
            break;
        case '/family':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/family 123456789012</code>"); return; }
            processLookupRequest($chatId, $userId, 'family', $args[0], $isGroup);
            break;
        case '/lpg':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/lpg 1234567890</code>"); return; }
            processLookupRequest($chatId, $userId, 'lpg', $args[0], $isGroup);
            break;
        case '/paytm':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/paytm example@ptyes</code>"); return; }
            processLookupRequest($chatId, $userId, 'paytm', $args[0], $isGroup);
            break;
        case '/pan':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/pan ABCDE1234F</code>"); return; }
            processLookupRequest($chatId, $userId, 'pan', $args[0], $isGroup);
            break;
        case '/gst':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/gst 22AAAAA0000A1Z5</code>"); return; }
            processLookupRequest($chatId, $userId, 'gst', $args[0], $isGroup);
            break;
        case '/pangst':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/pangst ABCDE1234F</code>"); return; }
            processLookupRequest($chatId, $userId, 'pangst', $args[0], $isGroup);
            break;
        case '/vehicle':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/vehicle MH01AB1234</code>"); return; }
            processLookupRequest($chatId, $userId, 'vehicle', $args[0], $isGroup);
            break;
        case '/vnum':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/vnum MH01AB1234</code>"); return; }
            processLookupRequest($chatId, $userId, 'vnum', $args[0], $isGroup);
            break;
        case '/mob2veh':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/mob2veh 9876543210</code>"); return; }
            processLookupRequest($chatId, $userId, 'mob2veh', $args[0], $isGroup);
            break;
        case '/challan':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/challan MH01AB1234</code>"); return; }
            processLookupRequest($chatId, $userId, 'challan', $args[0], $isGroup);
            break;
        case '/chassis':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/chassis ABC1234567890</code>"); return; }
            processLookupRequest($chatId, $userId, 'chassis', $args[0], $isGroup);
            break;
        case '/engine':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/engine ABC1234567890</code>"); return; }
            processLookupRequest($chatId, $userId, 'engine', $args[0], $isGroup);
            break;
        case '/ip':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/ip 192.168.1.1</code>"); return; }
            processLookupRequest($chatId, $userId, 'ip', $args[0], $isGroup);
            break;
        case '/pincode':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/pincode 400001</code>"); return; }
            processLookupRequest($chatId, $userId, 'pincode', $args[0], $isGroup);
            break;
        case '/tg':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/tg 9876543210</code>"); return; }
            processLookupRequest($chatId, $userId, 'telegram', $args[0], $isGroup);
            break;
        case '/insta':
        case '/ig':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/ig username</code>"); return; }
            processLookupRequest($chatId, $userId, 'instagram', $args[0], $isGroup);
            break;
        case '/ifsc':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/ifsc SBIN0001234</code>"); return; }
            processLookupRequest($chatId, $userId, 'ifsc', $args[0], $isGroup);
            break;
        case '/ff':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/ff 1234567890</code>"); return; }
            processLookupRequest($chatId, $userId, 'freefire', $args[0], $isGroup);
            break;
        case '/rc':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/rc MH01AB1234</code>"); return; }
            processLookupRequest($chatId, $userId, 'vehicle', $args[0], $isGroup);
            break;
        case '/ration':
            if (empty($args)) { sendMessage($chatId, "❌ Format: <code>/ration 123456789012</code>"); return; }
            processLookupRequest($chatId, $userId, 'ration', $args[0], $isGroup);
            break;
        default:
            if (strpos($text, '/') === 0) {
                if (!checkForceJoin($userId)) {
                    sendForceJoinMessage($chatId);
                    return;
                }
                sendMessage($chatId, "❓ Unknown command. Use /help to see available commands.");
            }
            break;
    }
}

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
