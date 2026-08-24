<?php
error_reporting(E_ALL);
ini_set('display_errors', 0);

$BOT_TOKEN = "8976716184:AAEqRWRNmVZ1hrAv8jbB5gvDi_ByczgPZU8";
$BOT_USERNAME = "@GauravDetailsBot";
$ADMIN_IDS = ["7255220723"];
$FORCE_CHANNEL = "@ZephrexXx_Portal2";
$LOG_CHANNEL = "@CyberTraceX_Logs";
$API_KEY = "ZEPH-K2L1P8";
$FAM_API_KEY = "FAM_49369415eefe95c67d87f1dd0879712c1baf5916f0fca390";
$FREE_CREDITS = 2;
$REFER_BONUS = 2;
$COOLDOWN = 3;
$UPI_ID = "gaurav.intel@fam";

$CREDIT_PLANS = [
    "10" => ["price" => 50, "credits" => 10, "display" => "₹50 — 10 CREDITS"],
    "20" => ["price" => 100, "credits" => 20, "display" => "₹100 — 20 CREDITS"],
    "40" => ["price" => 200, "credits" => 40, "display" => "₹200 — 40 CREDITS"],
    "50" => ["price" => 250, "credits" => 50, "display" => "₹250 — 50 CREDITS"],
    "100" => ["price" => 500, "credits" => 100, "display" => "₹500 — 100 CREDITS"],
    "unlimited" => ["price" => 3200, "credits" => "UNLIMITED", "display" => "₹3200 — UNLIMITED CREDIT"]
];

$API_ENDPOINTS = [
    'mobile' => "https://api-sell-phi.vercel.app/api?key={key}&type=NUM&term={term}",
    'aadhaar' => "https://api-sell-phi.vercel.app/api?key={key}&type=AADHAAR&term={term}",
    'family' => "https://api-sell-phi.vercel.app/api?key={key}&type=FAMILY&term={term}",
    'lpg' => "https://api-sell-phi.vercel.app/api?key={key}&type=LPG&term={term}",
    'ifsc' => "https://api-sell-phi.vercel.app/api?key={key}&type=IFSC&term={term}",
    'ip' => "https://api-sell-phi.vercel.app/api?key={key}&type=IP&term={term}",
    'telegram' => "https://api-sell-phi.vercel.app/api?key={key}&type=TGNUM&term={term}",
    'paytm' => "https://api-sell-phi.vercel.app/api?key={key}&type=PAYTM&term={term}",
    'pincode' => "https://api-sell-phi.vercel.app/api?key={key}&type=PINCODE&term={term}",
    'freefire' => "https://api-sell-phi.vercel.app/api?key={key}&type=FREEFIRE&term={term}",
    'vehicle' => "https://api-sell-phi.vercel.app/api?key={key}&type=VEHICLE&term={term}",
    'challan' => "https://api-sell-phi.vercel.app/api?key={key}&type=CHALLAN&term={term}",
    'instagram' => "https://api-sell-phi.vercel.app/api?key={key}&type=INSTAGRAM&term={term}",
    'vnum' => "https://api-sell-phi.vercel.app/api?key={key}&type=VNUM&term={term}",
    'pangst' => "https://api-sell-phi.vercel.app/api?key={key}&type=PANGST&term={term}",
    'gst' => "https://api-sell-phi.vercel.app/api?key={key}&type=GST&term={term}",
    'pan' => "https://api-sell-phi.vercel.app/api?key={key}&type=PAN&term={term}"
];

$FAM_QR_API = "https://fampay.anujbots.xyz/qr.php";
$FAM_VERIFY_API = "https://fampay.anujbots.xyz/verify.php";
$SUCCESS_IMAGE = "https://t.me/ZephrexXx_media/21";
$FAILED_IMAGE = "https://t.me/ZephrexXx_media/23";
$WELCOME_IMAGE = "https://t.me/ZephrexXx_media/27";

function initDatabase() {
    $dbFile = '/tmp/bot_database.json';
    if (!file_exists($dbFile)) {
        $initialData = ['users' => [], 'history' => [], 'user_states' => [], 'payment_stats' => ['today_income' => 0, 'total_income' => 0, 'plan_counts' => [], 'today_date' => date('Y-m-d')], 'pending_payments' => []];
        file_put_contents($dbFile, json_encode($initialData));
    }
    return $dbFile;
}

function loadDatabase() {
    $dbFile = initDatabase();
    $data = json_decode(file_get_contents($dbFile), true);
    if (!$data) $data = ['users' => [], 'history' => [], 'user_states' => [], 'pending_payments' => []];
    if (!isset($data['pending_payments'])) $data['pending_payments'] = [];
    return $data;
}

function saveDatabase($data) {
    file_put_contents('/tmp/bot_database.json', json_encode($data));
}

function getUser($userId) {
    $db = loadDatabase();
    $userId = (string)$userId;
    return isset($db['users'][$userId]) ? $db['users'][$userId] : null;
}

function createUser($userId, $name, $username, $referredBy = null) {
    $db = loadDatabase();
    $userId = (string)$userId;
    if (!isset($db['users'][$userId])) {
        $db['users'][$userId] = ['user_id' => $userId, 'name' => $name, 'username' => $username, 'credits' => (string)$GLOBALS['FREE_CREDITS'], 'joined_date' => date('Y-m-d H:i:s'), 'banned' => 0, 'last_request' => 0, 'referral_code' => 'REF' . $userId, 'referred_by' => $referredBy];
        if ($referredBy) {
            $referrer = getUser($referredBy);
            if ($referrer && $referrer['credits'] !== 'UNLIMITED') {
                $current = is_numeric($referrer['credits']) ? (int)$referrer['credits'] : 0;
                $db['users'][(string)$referredBy]['credits'] = (string)($current + $GLOBALS['REFER_BONUS']);
            }
        }
        saveDatabase($db);
    }
    return getUser($userId);
}

function updateUserCredits($userId, $creditsToAdd) {
    $db = loadDatabase();
    $userId = (string)$userId;
    if (isset($db['users'][$userId])) {
        if ($db['users'][$userId]['credits'] === 'UNLIMITED') return true;
        $current = is_numeric($db['users'][$userId]['credits']) ? (int)$db['users'][$userId]['credits'] : 0;
        $db['users'][$userId]['credits'] = (string)($current + $creditsToAdd);
        saveDatabase($db);
        return true;
    }
    return false;
}

function setUnlimitedCredits($userId) {
    $db = loadDatabase();
    if (isset($db['users'][(string)$userId])) { $db['users'][(string)$userId]['credits'] = 'UNLIMITED'; saveDatabase($db); }
}

function removeUnlimitedCredits($userId) {
    $db = loadDatabase();
    if (isset($db['users'][(string)$userId])) { $db['users'][(string)$userId]['credits'] = '0'; saveDatabase($db); }
}

function deductCredit($userId) {
    $db = loadDatabase();
    $userId = (string)$userId;
    if (isset($db['users'][$userId])) {
        if ($db['users'][$userId]['credits'] === 'UNLIMITED') return true;
        if (is_numeric($db['users'][$userId]['credits']) && (int)$db['users'][$userId]['credits'] > 0) {
            $db['users'][$userId]['credits'] = (string)((int)$db['users'][$userId]['credits'] - 1);
            saveDatabase($db);
            return true;
        }
    }
    return false;
}

function updateLastRequest($userId) {
    $db = loadDatabase();
    if (isset($db['users'][(string)$userId])) { $db['users'][(string)$userId]['last_request'] = time(); saveDatabase($db); }
}

function checkCooldown($userId) {
    $user = getUser($userId);
    if ($user) { $diff = time() - $user['last_request']; if ($diff < $GLOBALS['COOLDOWN']) return $GLOBALS['COOLDOWN'] - $diff; }
    return 0;
}

function isAdmin($userId) { return in_array((string)$userId, $GLOBALS['ADMIN_IDS']); }

function hasSufficientCredits($userId) {
    $user = getUser($userId);
    if (!$user) return false;
    if ($user['credits'] === 'UNLIMITED') return true;
    return is_numeric($user['credits']) && (int)$user['credits'] > 0;
}

function addHistory($userId, $action, $query, $resultCount) {
    $db = loadDatabase();
    $db['history'][] = ['user_id' => (string)$userId, 'action' => $action, 'query' => $query, 'result_count' => $resultCount, 'timestamp' => date('Y-m-d H:i:s')];
    if (count($db['history']) > 1000) $db['history'] = array_slice($db['history'], -1000);
    saveDatabase($db);
}

function setUserState($userId, $action, $data = "") {
    $db = loadDatabase();
    $db['user_states'][(string)$userId] = ['action' => $action, 'data' => $data];
    saveDatabase($db);
}

function getUserState($userId) {
    $db = loadDatabase();
    return isset($db['user_states'][(string)$userId]) ? $db['user_states'][(string)$userId] : null;
}

function clearUserState($userId) {
    $db = loadDatabase();
    unset($db['user_states'][(string)$userId]);
    saveDatabase($db);
}

function updateStats($planKey = null, $amount = 0) {
    $db = loadDatabase();
    $today = date('Y-m-d');
    if (!isset($db['payment_stats']) || $db['payment_stats']['today_date'] !== $today) {
        $db['payment_stats'] = ['today_income' => 0, 'total_income' => $db['payment_stats']['total_income'] ?? 0, 'plan_counts' => [], 'today_date' => $today];
    }
    if ($planKey && $amount) {
        $db['payment_stats']['today_income'] += $amount;
        $db['payment_stats']['total_income'] = ($db['payment_stats']['total_income'] ?? 0) + $amount;
        $db['payment_stats']['plan_counts'][$planKey] = ($db['payment_stats']['plan_counts'][$planKey] ?? 0) + 1;
    }
    saveDatabase($db);
}

function getStats() {
    $db = loadDatabase();
    return $db['payment_stats'] ?? ['today_income' => 0, 'total_income' => 0, 'plan_counts' => [], 'today_date' => date('Y-m-d')];
}

function val($v) { return ($v === null || $v === "" || $v === "null" || $v === "N/A" || $v === "None") ? "" : (string)$v; }

function formatAddress($addr) {
    if (!$addr) return "";
    $parts = array_filter(array_map('trim', explode("!", $addr)), function($p) { return $p !== "" && $p !== "NA" && $p !== "null"; });
    return implode(", ", $parts);
}

function is_valid_response($data) {
    if ($data === null) return false;
    if (is_array($data)) {
        if (isset($data['status']) && $data['status'] === false) return false;
        if (isset($data['data']) && empty($data['data'])) return false;
        return count($data) > 0;
    }
    return is_string($data) && trim($data) !== "";
}

function has_actual_data($data) {
    if (is_array($data)) {
        if (isset($data['status']) && $data['status'] === false) return false;
        $inner = $data['data'] ?? $data;
        if (is_array($inner)) {
            $results = $inner['results'] ?? $inner;
            if (is_array($results) && count($results) > 0) return true;
            foreach ($inner as $k => $v) {
                if (in_array($k, ['status', 'cached', 'response_time', 'status_code', 'http_status', 'Message', 'message', 'rs', 'rc', 'rd'])) continue;
                if (is_array($v)) { if (has_actual_data(['data' => $v])) return true; }
                elseif ($v !== null && $v !== "" && $v !== "null" && $v !== "N/A") return true;
            }
        }
    }
    return false;
}

function extract_data_for_type($type, $response) {
    $data = $response['data'] ?? $response;
    switch ($type) {
        case 'mobile': case 'aadhaar': return $data['results'] ?? $data;
        case 'family': return is_array($data) && !isset($data['results']) ? $data : ($data['results'] ?? $data);
        case 'lpg': 
            $innerData = $data['data'] ?? $data;
            return $innerData['pd'] ?? $innerData;
        case 'paytm': case 'pangst': case 'gst': return $data['data'] ?? $data;
        case 'pan': return $data['results'] ?? $data;
        case 'vehicle': return $data['response'] ?? $data;
        case 'vnum': case 'telegram': case 'instagram': return $data;
        case 'challan':
            $challans = is_array($data['data'] ?? null) ? $data['data'] : [];
            $rcInfo = is_array($data['rc_info'] ?? null) ? $data['rc_info'] : [];
            $pending = [];
            foreach ($challans as $c) {
                if (!is_array($c)) continue;
                $offences = [];
                foreach (($c['offece'] ?? []) as $o) if (is_array($o) && isset($o['offence_name'])) $offences[] = $o['offence_name'];
                $pending[] = ['challan_no' => $c['challan_no'] ?? '', 'date' => $c['challan_date'] ?? '', 'amount' => $c['challan_amount'] ?? '', 'state' => $c['state_code'] ?? '', 'status' => $c['challan_status'] ?? '', 'violator_name' => $c['violator_name'] ?? '', 'offence' => $offences];
            }
            return ['reg_no' => $challans[0]['reg_no'] ?? null, 'owner_name' => $rcInfo['owner_name'] ?? '', 'vehicle' => $rcInfo['maker_modal'] ?? '', 'insurance_upto' => '', 'pending_challans' => $pending];
        case 'pincode': return $data['PostOffice'] ?? [];
        case 'ip': case 'ifsc': case 'freefire': return $data['results'] ?? $data;
        default: return $data;
    }
}

function validateMobile($d) { if (!is_array($d) || count($d) === 0) return false; foreach ($d as $e) { if (!is_array($e)) continue; $m = $e['mobile'] ?? ($e['MOBILE'] ?? $e['num'] ?? null); if ($m && !in_array(trim((string)$m), ['', 'null', 'N/A'])) return true; } return false; }
function validateFamily($d) { if (!is_array($d) || count($d) === 0) return false; $c = 0; foreach ($d as $m) { if (!is_array($m)) continue; $n = $m['memberName'] ?? null; if ($n && !in_array(trim((string)$n), ['', 'null', 'N/A', 'None'])) $c++; } return $c > 0; }
function validateAadhaar($d) { if (is_array($d) && isset($d['id'])) $d = [$d]; if (!is_array($d) || count($d) === 0) return false; foreach ($d as $e) { if (!is_array($e) || !isset($e['id']) || in_array(trim((string)$e['id']), ['', 'null', 'N/A']) || !isset($e['name']) || in_array(trim((string)$e['name']), ['', 'null', 'N/A'])) return false; } return true; }
function validateVehicle($d) { return is_array($d) && isset($d['regNo']) && !in_array(trim((string)$d['regNo']), ['', 'null', 'N/A']) && isset($d['vehicle']) && !in_array(trim((string)$d['vehicle']), ['', 'null', 'N/A']); }
function validateLpg($d) { if (!is_array($d)) return false; $c = $d['ConsumerDet'] ?? []; return isset($c['ConsumerName']) && !in_array(trim((string)$c['ConsumerName']), ['', 'null', 'N/A']) && isset($c['ConsumerNo']) && !in_array(trim((string)$c['ConsumerNo']), ['', 'null', 'N/A']); }
function validatePaytm($d) { return is_array($d) && isset($d['name']) && !in_array(trim((string)$d['name']), ['', 'null', 'N/A']) && isset($d['phoneNumber']) && !in_array(trim((string)$d['phoneNumber']), ['', 'null', 'N/A']); }
function validateInstagram($d) { if (!is_array($d)) return false; $p = $d['profile'] ?? []; return isset($p['username']) && !in_array(trim((string)$p['username']), ['', 'null', 'N/A']); }
function validateFreefire($d) { return is_array($d) && isset($d['id']) && !in_array(trim((string)$d['id']), ['', 'null', 'N/A']) && isset($d['nickname']) && !in_array(trim((string)$d['nickname']), ['', 'null', 'N/A']); }
function validatePan($d) { return is_array($d) && isset($d['pan_number']) && !in_array(trim((string)$d['pan_number']), ['', 'null', 'N/A']) && isset($d['name']) && !in_array(trim((string)$d['name']), ['', 'null', 'N/A']); }
function validatePanToGst($d) { if (!is_array($d) || !isset($d['pan']) || in_array(trim((string)$d['pan']), ['', 'null', 'N/A'])) return false; $g = $d['gstins'] ?? []; if (!is_array($g) || count($g) === 0) return false; foreach ($g as $x) if (!is_array($x) || !isset($x['gstin']) || in_array(trim((string)$x['gstin']), ['', 'null', 'N/A'])) return false; return true; }
function validateIfsc($d) { return is_array($d) && isset($d['IFSC']) && !in_array(trim((string)$d['IFSC']), ['', 'null', 'N/A']) && isset($d['BANK']) && !in_array(trim((string)$d['BANK']), ['', 'null', 'N/A']); }
function validatePincode($d) { if (!is_array($d) || count($d) === 0) return false; $f = $d[0]; return is_array($f) && isset($f['Pincode']) && !in_array(trim((string)$f['Pincode']), ['', 'null', 'N/A']) && isset($f['Name']) && !in_array(trim((string)$f['Name']), ['', 'null', 'N/A']); }
function validateTelegram($d) { return is_array($d) && isset($d['number']) && !in_array(trim((string)$d['number']), ['', 'null', 'N/A']) && isset($d['tg_id']) && !in_array(trim((string)$d['tg_id']), ['', 'null', 'N/A']); }
function validateGst($d) { return is_array($d) && isset($d['Gstin']) && !in_array(trim((string)$d['Gstin']), ['', 'null', 'N/A']) && isset($d['TradeName']) && !in_array(trim((string)$d['TradeName']), ['', 'null', 'N/A']) && isset($d['LegalName']) && !in_array(trim((string)$d['LegalName']), ['', 'null', 'N/A']); }
function validateVnum($d) { return is_array($d) && isset($d['mobile']) && !in_array(trim((string)$d['mobile']), ['', 'null', 'N/A']) && isset($d['vehicle']) && !in_array(trim((string)$d['vehicle']), ['', 'null', 'N/A']); }
function validateChallan($d) { if (!is_array($d) || !isset($d['reg_no']) || in_array(trim((string)$d['reg_no']), ['', 'null', 'N/A'])) return false; $c = $d['pending_challans'] ?? []; if (!is_array($c) || count($c) === 0) return false; foreach ($c as $x) if (!is_array($x) || !isset($x['challan_no']) || in_array(trim((string)$x['challan_no']), ['', 'null', 'N/A'])) return false; return true; }
function validateIp($d) { return is_array($d) && isset($d['query']) && !in_array(trim((string)$d['query']), ['', 'null', 'N/A']) && isset($d['country']) && !in_array(trim((string)$d['country']), ['', 'null', 'N/A']); }

function formatLpg($data, $credits) {
    $consumer = $data['ConsumerDet'] ?? [];
    $consumerAddr = $consumer['ConsumerAddress'] ?? [];
    $distributor = $data['DistributorDet'] ?? [];
    $distributorAddr = $distributor['DistributorAddress'] ?? [];
    $asset = $data['AssetDet'] ?? [];
    $products = $asset['ProductDet'] ?? [];
    $ptdDet = $data['PTDDet'] ?? [];
    
    $msg = "🛢️ <b>LPG CONSUMER INFORMATION</b>\n━━━━━━━━━━━━━━━━━━━━━━━\n";
    
    if (!empty($consumer['ConsumerName'])) $msg .= "👤 <b>CONSUMER NAME:</b> <code>" . val($consumer['ConsumerName']) . "</code>\n";
    if (!empty($consumer['ConsumerId'])) $msg .= "🆔 <b>CONSUMER ID:</b> <code>" . val($consumer['ConsumerId']) . "</code>\n";
    if (!empty($consumer['ConsumerNo'])) $msg .= "🔢 <b>CONSUMER NO:</b> <code>" . val($consumer['ConsumerNo']) . "</code>\n";
    if (!empty($consumer['ConsumerMobile'])) $msg .= "📞 <b>MOBILE:</b> <code>" . val($consumer['ConsumerMobile']) . "</code>\n";
    if (!empty($consumer['ConsumerRelType'])) $msg .= "🏷️ <b>RELATION TYPE:</b> <code>" . val($consumer['ConsumerRelType']) . "</code>\n";
    
    $msg .= "━━━━━━━━━━━━━━━━━━━━━━━\n";
    
    if (!empty($consumer['ConsumerStatus'])) $msg .= "📊 <b>STATUS:</b> <code>" . val($consumer['ConsumerStatus']) . "</code>\n";
    if (!empty($consumer['ConsumerSubStatus'])) $msg .= "📊 <b>SUB STATUS:</b> <code>" . val($consumer['ConsumerSubStatus']) . "</code>\n";
    if (!empty($consumer['ConsumerCategory'])) $msg .= "🏷️ <b>CATEGORY:</b> <code>" . val($consumer['ConsumerCategory']) . "</code>\n";
    if (!empty($consumer['ConsumerType'])) $msg .= "🔗 <b>TYPE:</b> <code>" . val($consumer['ConsumerType']) . "</code>\n";
    if (!empty($consumer['MIDueDate'])) $msg .= "📅 <b>MI DUE DATE:</b> <code>" . val($consumer['MIDueDate']) . "</code>\n";
    if (!empty($consumer['TubeChangeDate'])) $msg .= "🔧 <b>TUBE CHANGE DATE:</b> <code>" . val($consumer['TubeChangeDate']) . "</code>\n";
    if (!empty($consumer['TubeChangeDueDate'])) $msg .= "🔧 <b>TUBE CHANGE DUE:</b> <code>" . val($consumer['TubeChangeDueDate']) . "</code>\n";
    
    $hasAddr = false;
    foreach (['AddressLine1', 'AddressLine2', 'AddressLine3', 'City', 'District', 'State', 'Pincode', 'Country'] as $k) {
        if (!empty($consumerAddr[$k])) { $hasAddr = true; break; }
    }
    if ($hasAddr) {
        $msg .= "━━━━━━━━━━━━━━━━━━━━━━━\n🏠 <b>CONSUMER ADDRESS:</b>\n";
        if (!empty($consumerAddr['AddressLine1'])) $msg .= "📍 <b>Line1:</b> <code>" . val($consumerAddr['AddressLine1']) . "</code>\n";
        if (!empty($consumerAddr['AddressLine2'])) $msg .= "📍 <b>Line2:</b> <code>" . val($consumerAddr['AddressLine2']) . "</code>\n";
        if (!empty($consumerAddr['AddressLine3'])) $msg .= "📍 <b>Line3:</b> <code>" . val($consumerAddr['AddressLine3']) . "</code>\n";
        if (!empty($consumerAddr['City'])) $msg .= "🏙️ <b>City:</b> <code>" . val($consumerAddr['City']) . "</code>\n";
        if (!empty($consumerAddr['District'])) $msg .= "🗺️ <b>District:</b> <code>" . val($consumerAddr['District']) . "</code>\n";
        if (!empty($consumerAddr['State'])) $msg .= "🌐 <b>State:</b> <code>" . val($consumerAddr['State']) . "</code>\n";
        if (!empty($consumerAddr['Pincode'])) $msg .= "📮 <b>Pincode:</b> <code>" . val($consumerAddr['Pincode']) . "</code>\n";
        if (!empty($consumerAddr['Country'])) $msg .= "🌍 <b>Country:</b> <code>" . val($consumerAddr['Country']) . "</code>\n";
    }
    
    $hasDist = false;
    foreach (['DistributorName', 'DistributorContact', 'DistributorCode', 'DistributorBacklogDays'] as $k) {
        if (!empty($distributor[$k])) { $hasDist = true; break; }
    }
    if ($hasDist) {
        $msg .= "━━━━━━━━━━━━━━━━━━━━━━━\n🏢 <b>DISTRIBUTOR INFO:</b>\n";
        if (!empty($distributor['DistributorName'])) $msg .= "🏬 <b>Name:</b> <code>" . val($distributor['DistributorName']) . "</code>\n";
        if (!empty($distributor['DistributorContact'])) $msg .= "📞 <b>Contact:</b> <code>" . val($distributor['DistributorContact']) . "</code>\n";
        if (!empty($distributor['DistributorCode'])) $msg .= "🔢 <b>Code:</b> <code>" . val($distributor['DistributorCode']) . "</code>\n";
        if (!empty($distributor['DistributorBacklogDays'])) $msg .= "⏳ <b>Backlog Days:</b> <code>" . val($distributor['DistributorBacklogDays']) . "</code>\n";
        
        $hasDistAddr = false;
        foreach (['AddressLine1', 'AddressLine2', 'AddressLine3', 'City', 'District', 'State', 'Pincode', 'Country'] as $k) {
            if (!empty($distributorAddr[$k])) { $hasDistAddr = true; break; }
        }
        if ($hasDistAddr) {
            $msg .= "📍 <b>DISTRIBUTOR ADDRESS:</b>\n";
            if (!empty($distributorAddr['AddressLine1'])) $msg .= "🏢 <b>Line1:</b> <code>" . val($distributorAddr['AddressLine1']) . "</code>\n";
            if (!empty($distributorAddr['AddressLine2'])) $msg .= "🏢 <b>Line2:</b> <code>" . val($distributorAddr['AddressLine2']) . "</code>\n";
            if (!empty($distributorAddr['AddressLine3'])) $msg .= "🏢 <b>Line3:</b> <code>" . val($distributorAddr['AddressLine3']) . "</code>\n";
            if (!empty($distributorAddr['City'])) $msg .= "🏙️ <b>City:</b> <code>" . val($distributorAddr['City']) . "</code>\n";
            if (!empty($distributorAddr['District'])) $msg .= "🗺️ <b>District:</b> <code>" . val($distributorAddr['District']) . "</code>\n";
            if (!empty($distributorAddr['State'])) $msg .= "🌐 <b>State:</b> <code>" . val($distributorAddr['State']) . "</code>\n";
            if (!empty($distributorAddr['Pincode'])) $msg .= "📮 <b>Pincode:</b> <code>" . val($distributorAddr['Pincode']) . "</code>\n";
            if (!empty($distributorAddr['Country'])) $msg .= "🌍 <b>Country:</b> <code>" . val($distributorAddr['Country']) . "</code>\n";
        }
    }
    
    if (count($products) > 0) {
        $msg .= "━━━━━━━━━━━━━━━━━━━━━━━\n🛒 <b>PRODUCTS:</b>\n";
        foreach ($products as $p) {
            if (!is_array($p)) continue;
            if (!empty($p['ProductName'])) $msg .= "📦 <b>Product:</b> <code>" . val($p['ProductName']) . "</code>\n";
            if (!empty($p['Quantity'])) $msg .= "🔢 <b>Quantity:</b> <code>" . val($p['Quantity']) . "</code>\n";
            if (!empty($p['UnitSize'])) $msg .= "📏 <b>Unit Size:</b> <code>" . val($p['UnitSize']) . " Kg</code>\n";
            $priceDet = $p['ProductPriceDet'] ?? [];
            if (!empty($priceDet['RSP'])) $msg .= "💰 <b>RSP:</b> <code>₹" . val($priceDet['RSP']) . "</code>\n";
            if (!empty($priceDet['SubsidyAmount'])) $msg .= "💸 <b>Subsidy:</b> <code>₹" . val($priceDet['SubsidyAmount']) . "</code>\n";
            $msg .= "─────────────────────\n";
        }
    }
    
    $msg .= "━━━━━━━━━━━━━━━━━━━━━━━\n";
    if (!empty($data['ConsumedQuota'])) $msg .= "📦 <b>CONSUMED QUOTA:</b> <code>" . val($data['ConsumedQuota']) . " Kg</code>\n";
    if (!empty($data['SchemeOpted'])) $msg .= "💳 <b>SCHEME:</b> <code>" . val($data['SchemeOpted']) . "</code>\n";
    if (!empty($data['eKYCFlag'])) $msg .= "🔐 <b>eKYC:</b> <code>" . val($data['eKYCFlag']) . "</code>\n";
    if (!empty($data['AuthType'])) $msg .= "🔑 <b>AUTH TYPE:</b> <code>" . val($data['AuthType']) . "</code>\n";
    if (!empty($data['Source'])) $msg .= "📡 <b>SOURCE:</b> <code>" . val($data['Source']) . "</code>\n";
    if (!empty($data['BookingEligible'])) $msg .= "📅 <b>BOOKING ELIGIBLE:</b> <code>" . val($data['BookingEligible']) . "</code>\n";
    if (!empty($data['BookingEligibilityFailureReason'])) $msg .= "⚠️ <b>BOOKING NOTE:</b> <code>" . val($data['BookingEligibilityFailureReason']) . "</code>\n";
    
    if (!empty($ptdDet['TimeRange']) || !empty($ptdDet['DayPreference'])) {
        $msg .= "━━━━━━━━━━━━━━━━━━━━━━━\n📅 <b>DELIVERY PREFERENCE:</b>\n";
        if (!empty($ptdDet['TimeRange'])) $msg .= "🕐 <b>Time:</b> <code>" . val($ptdDet['TimeRange']) . "</code>\n";
        if (!empty($ptdDet['DayPreference'])) $msg .= "📆 <b>Day:</b> <code>" . val($ptdDet['DayPreference']) . "</code>\n";
    }
    
    $msg .= "━━━━━━━━━━━━━━━━━━━━━━━\n💰 <b>CREDITS REMAINING:</b> <code>$credits</code>";
    return $msg;
}

function formatPaytm($d, $c) { 
    $p = $d['profileUrl'] ?? null; 
    $pt = $p ? "<a href='$p'>Click Here</a>" : ""; 
    return "💳 <b>PAYTM USER INFORMATION</b>\n━━━━━━━━━━━━━━━━━━━━━━━\n👤 <b>NAME:</b> <code>" . val($d['name'] ?? null) . "</code>\n📞 <b>PHONE NUMBER:</b> <code>" . val($d['phoneNumber'] ?? null) . "</code>\n🔗 <b>VPA:</b> <code>" . val($d['vpa'] ?? null) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n🖼️ <b>PROFILE PIC:</b> $pt\n━━━━━━━━━━━━━━━━━━━━━━━\n💰 <b>CREDITS REMAINING:</b> <code>$c</code>";
}

function formatFamily($dl, $c) { $vm = []; foreach ($dl as $m) { $n = $m['memberName'] ?? null; if ($n && !in_array(trim((string)$n), ['', 'null', 'N/A', 'None'])) $vm[] = $m; } $msg = "👨‍👩‍👧‍👦 <b>FAMILY INFORMATION</b>\n━━━━━━━━━━━━━━━━━━━━━━━\n📊 <b>TOTAL MEMBERS:</b> <code>" . count($vm) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n"; foreach ($vm as $i => $m) { $hb = ($m['familyHead'] ?? '') === 'Yes' ? ' 👑 (HEAD)' : ''; $msg .= "👤 <b>MEMBER #" . ($i + 1) . "$hb</b>\n📛 <b>Name:</b> <code>" . val($m['memberName'] ?? null) . "</code>\n🆔 <b>Ration Card ID:</b> <code>" . val($m['rcId'] ?? null) . "</code>\n🏪 <b>FPS ID:</b> <code>" . val($m['fpsId'] ?? null) . "</code>\n🔒 <b>Aadhaar:</b> <code>" . val($m['aadhaar'] ?? null) . "</code>\n🌐 <b>State:</b> <code>" . val($m['state'] ?? null) . "</code>\n🏙️ <b>District:</b> <code>" . val($m['district'] ?? null) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n"; } $msg .= "💰 <b>CREDITS REMAINING:</b> <code>$c</code>"; return $msg; }
function formatTelegram($d, $c) { return "📱 <b>TELEGRAM LOOKUP</b>\n━━━━━━━━━━━━━━━━━━━━━━━\n📞 <b>NUMBER:</b> <code>" . val($d['number'] ?? null) . "</code>\n🔢 <b>COUNTRY CODE:</b> <code>" . val($d['country_code'] ?? null) . "</code>\n🌍 <b>COUNTRY:</b> <code>" . val($d['country'] ?? null) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n🆔 <b>TELEGRAM ID:</b> <code>" . val($d['tg_id'] ?? null) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n💰 <b>CREDITS REMAINING:</b> <code>$c</code>"; }
function formatVnum($d, $c) { return "🚗 <b>VNUM INFORMATION</b>\n━━━━━━━━━━━━━━━━━━━━━━━\n🔢 <b>VEHICLE NO:</b> <code>" . val($d['vehicle'] ?? null) . "</code>\n📞 <b>MOBILE:</b> <code>" . val($d['mobile'] ?? null) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n💰 <b>CREDITS REMAINING:</b> <code>$c</code>"; }
function formatVehicle($d, $c) { $rto = $d['rtoData'] ?? []; return "🚗 <b>VEHICLE INFORMATION</b>\n━━━━━━━━━━━━━━━━━━━━━━━\n🔢 <b>VEHICLE NO:</b> <code>" . val($d['regNo'] ?? null) . "</code>\n👤 <b>OWNER NAME:</b> <code>" . val($d['owner'] ?? null) . "</code>\n👨‍👦 <b>FATHER NAME:</b> <code>" . val($d['ownerFatherName'] ?? null) . "</code>\n📅 <b>REG DATE:</b> <code>" . val($d['regDate'] ?? null) . "</code>\n🏛️ <b>RTO:</b> <code>" . val($d['regAuthority'] ?? null) . "</code>\n🎫 <b>RTO CODE:</b> <code>" . val($d['rtoCode'] ?? null) . "</code>\n📍 <b>RTO ID:</b> <code>" . val($d['rtoId'] ?? null) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n🏭 <b>MAKE:</b> <code>" . val($d['manufacturer'] ?? null) . "</code>\n🚘 <b>MODEL:</b> <code>" . val($d['vehicle'] ?? null) . "</code>\n🔧 <b>VARIANT:</b> <code>" . val($d['variant'] ?? null) . "</code>\n⛽ <b>FUEL:</b> <code>" . val($d['fuelType'] ?? null) . "</code>\n🚦 <b>TYPE:</b> <code>" . val($d['vehicleType'] ?? null) . "</code>\n📊 <b>CATEGORY:</b> <code>" . val($d['vehicleClass'] ?? null) . "</code>\n🏢 <b>COMMERCIAL:</b> <code>" . (isset($d['isCommercial']) && $d['isCommercial'] ? 'YES' : 'NO') . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n🔩 <b>CHASSIS NO:</b> <code>" . val($d['chassis'] ?? null) . "</code>\n⚙️ <b>ENGINE NO:</b> <code>" . val($d['engine'] ?? null) . "</code>\n🔧 <b>CC:</b> <code>" . val($d['cubicCapacity'] ?? null) . "</code>\n💺 <b>SEAT CAPACITY:</b> <code>" . val($d['seatCapacity'] ?? null) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n🏭 <b>MFG YEAR:</b> <code>" . val($d['manufacturerYear'] ?? null) . "</code>\n🗓️ <b>MFG MONTH/YEAR:</b> <code>" . val($d['manufacturerMonthYear'] ?? null) . "</code>\n⏳ <b>VEHICLE AGE:</b> <code>" . val($d['vehicleAge'] ?? null) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n🏦 <b>FINANCER:</b> <code>" . val($d['financerName'] ?? null) . "</code>\n🛡️ <b>INSURER:</b> <code>" . val($d['insuranceCompanyName'] ?? null) . "</code>\n📄 <b>POLICY NO:</b> <code>" . val($d['insurancePolicyNumber'] ?? null) . "</code>\n📆 <b>POLICY EXPIRY:</b> <code>" . val($d['insuranceUpto'] ?? null) . "</code>\n❌ <b>POLICY EXPIRED:</b> <code>" . (isset($d['insuranceExpired']) && $d['insuranceExpired'] ? 'YES' : 'NO') . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n🌫️ <b>PUCC NO:</b> <code>" . val($d['puccNumber'] ?? null) . "</code>\n📅 <b>PUCC VALID UPTO:</b> <code>" . val($d['puccValidUpto'] ?? null) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n🏛️ <b>RTO OFFICE:</b> <code>" . val($rto['rtoName'] ?? null) . "</code>\n🌐 <b>RTO STATE:</b> <code>" . val($rto['statename'] ?? null) . "</code>\n🟢 <b>RTO STATUS:</b> <code>" . (isset($rto['isActive']) && $rto['isActive'] ? 'ACTIVE' : 'INACTIVE') . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n🏠 <b>PERMANENT ADDRESS:</b> <code>" . val($d['permAddress'] ?? null) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n📍 <b>PRESENT ADDRESS:</b> <code>" . val($d['presentAddress'] ?? null) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n💰 <b>CREDITS REMAINING:</b> <code>$c</code>"; }
function formatMobile($dl, $c) { $msg = "📱 <b>MOBILE INFORMATION</b>\n━━━━━━━━━━━━━━━━━━━━━━━\n📊 <b>TOTAL RESULTS:</b> <code>" . count($dl) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n"; foreach ($dl as $i => $d) { $mobile = $d['mobile'] ?? ($d['MOBILE'] ?? ($d['num'] ?? null)); $name = $d['name'] ?? ($d['NAME'] ?? null); $fname = $d['fname'] ?? ($d['FNAME'] ?? null); $address = $d['address'] ?? ($d['ADDRESS'] ?? null); $alt = $d['alt'] ?? null; $msg .= "📋 <b>RESULT #" . ($i + 1) . "</b>\n━━━━━━━━━━━━━━━━━━━━━━━\n📞 <b>MOBILE:</b> <code>" . val($mobile) . "</code>\n👤 <b>NAME:</b> <code>" . val($name) . "</code>\n👨‍👦 <b>FATHER NAME:</b> <code>" . val($fname) . "</code>\n"; if ($alt) $msg .= "📞 <b>ALT NUMBER:</b> <code>" . val($alt) . "</code>\n"; $msg .= "🆔 <b>AADHAAR NO:</b> <code>" . val($d['aadhar'] ?? ($d['id'] ?? null)) . "</code>\n📡 <b>CIRCLE:</b> <code>" . val($d['circle'] ?? null) . "</code>\n🏠 <b>ADDRESS:</b>\n<code>" . formatAddress($address) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n"; } $msg .= "💰 <b>CREDITS REMAINING:</b> <code>$c</code>"; return $msg; }
function formatInstagram($d, $c) { $p = $d['profile'] ?? []; $pic = $p['profile_pic_url_hd'] ?? null; $pt = $pic ? "<a href='$pic'>Click Here</a>" : ""; return "📸 <b>INSTAGRAM INFORMATION</b>\n━━━━━━━━━━━━━━━━━━━━━━━\n🆔 <b>ID:</b> <code>" . val($p['id'] ?? null) . "</code>\n👤 <b>USERNAME:</b> <code>@" . val($p['username'] ?? null) . "</code>\n📛 <b>FULL NAME:</b> <code>" . val($p['full_name'] ?? null) . "</code>\n📝 <b>BIO:</b> <code>" . val($p['biography'] ?? null) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n👥 <b>FOLLOWERS:</b> <code>" . val($p['followers'] ?? null) . "</code>\n➡️ <b>FOLLOWING:</b> <code>" . val($p['following'] ?? null) . "</code>\n🖼️ <b>POSTS:</b> <code>" . val($p['posts'] ?? null) . "</code>\n📅 <b>ACCOUNT CREATED:</b> <code>" . val($p['account_creation_year'] ?? null) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n🔒 <b>PRIVATE:</b> <code>" . (isset($p['is_private']) && $p['is_private'] ? 'YES' : 'NO') . "</code>\n✅ <b>VERIFIED:</b> <code>" . (isset($p['is_verified']) && $p['is_verified'] ? 'YES' : 'NO') . "</code>\n💼 <b>BUSINESS:</b> <code>" . (isset($p['is_business_account']) && $p['is_business_account'] ? 'YES' : 'NO') . "</code>\n🌟 <b>PROFESSIONAL:</b> <code>" . (isset($p['is_professional_account']) && $p['is_professional_account'] ? 'YES' : 'NO') . "</code>\n🏷️ <b>CATEGORY:</b> <code>" . val($p['category_name'] ?? null) . "</code>\n🔗 <b>EXTERNAL URL:</b> <code>" . val($p['external_url'] ?? null) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n🖼️ <b>PROFILE PIC:</b> $pt\n━━━━━━━━━━━━━━━━━━━━━━━\n🕒 <b>COLLECTED AT:</b> <code>" . val($d['collected_at'] ?? null) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n💰 <b>CREDITS REMAINING:</b> <code>$c</code>"; }
function formatFreefire($d, $c) { return "🎮 <b>FREE FIRE PROFILE</b>\n━━━━━━━━━━━━━━━━━━━━━━━\n🆔 <b>UID:</b> <code>" . val($d['id'] ?? null) . "</code>\n👤 <b>NICKNAME:</b> <code>" . val($d['nickname'] ?? null) . "</code>\n🌍 <b>REGION:</b> <code>" . val($d['region'] ?? null) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n⭐ <b>LEVEL:</b> <code>" . val($d['level'] ?? null) . "</code>\n🔥 <b>EXPERIENCE XP:</b> <code>" . val($d['experience_xp'] ?? null) . "</code>\n🏆 <b>RANKED POINTS:</b> <code>" . val($d['ranked_points'] ?? null) . "</code>\n❤️ <b>LIKES:</b> <code>" . val($d['likes'] ?? null) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n💎 <b>PRIME:</b> <code>" . val($d['prime'] ?? null) . "</code>\n👑 <b>INFLUENCER:</b> <code>" . (isset($d['influencer']) && $d['influencer'] ? 'YES' : 'NO') . "</code>\n👗 <b>SKINS:</b> <code>" . val($d['skins_equipadas'] ?? null) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n📝 <b>BIO:</b> <code>" . val($d['signature_bio'] ?? null) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n🕒 <b>LAST LOGIN:</b> <code>" . val($d['last_login'] ?? null) . "</code>\n📅 <b>ACCOUNT CREATED:</b> <code>" . val($d['account_created'] ?? null) . "</code>\n🔄 <b>PROFILE UPDATED:</b> <code>" . val($d['profile_updated'] ?? null) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n🗓️ <b>FETCHED ON:</b> <code>" . val($d['date'] ?? null) . " " . val($d['time'] ?? null) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n💰 <b>CREDITS REMAINING:</b> <code>$c</code>"; }
function formatPanDetail($d, $c) { $g = ($d['gender'] ?? '') === 'Male' ? '👨' : '👩'; return "🪪 <b>PAN DETAIL INFORMATION</b>\n━━━━━━━━━━━━━━━━━━━━━━━\n💳 <b>PAN NUMBER:</b> <code>" . val($d['pan_number'] ?? null) . "</code>\n📊 <b>PAN STATUS:</b> <code>" . val($d['pan_status'] ?? null) . "</code>\n✅ <b>IS VALID:</b> <code>" . (isset($d['is_valid']) && $d['is_valid'] ? 'YES' : 'NO') . "</code>\n🏷️ <b>CATEGORY:</b> <code>" . val($d['category'] ?? null) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n👤 <b>NAME:</b> <code>" . val($d['name'] ?? null) . "</code>\n🎂 <b>DOB:</b> <code>" . val($d['dob'] ?? null) . "</code>\n$g <b>GENDER:</b> <code>" . val($d['gender'] ?? null) . "</code>\n📞 <b>MOBILE NO:</b> <code>" . val($d['mobile_no'] ?? null) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n🔒 <b>AADHAAR NUMBER:</b> <code>" . val($d['aadhar_number'] ?? null) . "</code>\n🔗 <b>AADHAAR LINKED:</b> <code>" . (isset($d['aadhaar_linked']) && $d['aadhaar_linked'] ? '✅ YES' : '❌ NO') . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n💰 <b>CREDITS REMAINING:</b> <code>$c</code>"; }
function formatPanToGst($d, $c) { $g = $d['gstins'] ?? []; $msg = "🧾 <b>PAN TO GST INFORMATION</b>\n━━━━━━━━━━━━━━━━━━━━━━━\n💳 <b>PAN NUMBER:</b> <code>" . val($d['pan'] ?? null) . "</code>\n📊 <b>TOTAL GSTINs:</b> <code>" . val($d['total'] ?? null) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n🏢 <b>GSTIN LIST</b>\n━━━━━━━━━━━━━━━━━━━━━━━\n"; foreach ($g as $i => $x) { $st = isset($x['state']) && $x['state'] ? " — 📍 <i>{$x['state']}</i>" : ""; $msg .= "<b>#" . ($i + 1) . "</b> <code>" . val($x['gstin'] ?? null) . "</code>$st\n"; } $msg .= "━━━━━━━━━━━━━━━━━━━━━━━\n💰 <b>CREDITS REMAINING:</b> <code>$c</code>"; return $msg; }
function formatIfsc($d, $c) { return "🏦 <b>IFSC / BANK INFORMATION</b>\n━━━━━━━━━━━━━━━━━━━━━━━\n🏛️ <b>BANK:</b> <code>" . val($d['BANK'] ?? null) . "</code>\n🔤 <b>BANK CODE:</b> <code>" . val($d['BANKCODE'] ?? null) . "</code>\n🔢 <b>IFSC:</b> <code>" . val($d['IFSC'] ?? null) . "</code>\n🔢 <b>MICR:</b> <code>" . val($d['MICR'] ?? null) . "</code>\n🌐 <b>SWIFT:</b> <code>" . val($d['SWIFT'] ?? null) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n🏢 <b>BRANCH:</b> <code>" . val($d['BRANCH'] ?? null) . "</code>\n🏙️ <b>CITY:</b> <code>" . val($d['CITY'] ?? null) . "</code>\n📍 <b>CENTRE:</b> <code>" . val($d['CENTRE'] ?? null) . "</code>\n🗺️ <b>DISTRICT:</b> <code>" . val($d['DISTRICT'] ?? null) . "</code>\n🌐 <b>STATE:</b> <code>" . val($d['STATE'] ?? null) . "</code>\n🏳️ <b>ISO CODE:</b> <code>" . val($d['ISO3166'] ?? null) . "</code>\n📞 <b>CONTACT:</b> <code>" . val($d['CONTACT'] ?? null) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n🏠 <b>ADDRESS:</b> <code>" . val($d['ADDRESS'] ?? null) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n💳 <b>PAYMENT SERVICES</b>\n⚡ <b>UPI:</b> <code>" . (isset($d['UPI']) && $d['UPI'] ? '✅ YES' : '❌ NO') . "</code>\n🔄 <b>NEFT:</b> <code>" . (isset($d['NEFT']) && $d['NEFT'] ? '✅ YES' : '❌ NO') . "</code>\n🚀 <b>RTGS:</b> <code>" . (isset($d['RTGS']) && $d['RTGS'] ? '✅ YES' : '❌ NO') . "</code>\n📲 <b>IMPS:</b> <code>" . (isset($d['IMPS']) && $d['IMPS'] ? '✅ YES' : '❌ NO') . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n💰 <b>CREDITS REMAINING:</b> <code>$c</code>"; }
function formatPincode($o, $c) { $f = $o[0]; $msg = "📮 <b>PINCODE INFORMATION</b>\n━━━━━━━━━━━━━━━━━━━━━━━\n📌 <b>PINCODE:</b> <code>" . val($f['Pincode'] ?? null) . "</code>\n🏙️ <b>DISTRICT:</b> <code>" . val($f['District'] ?? null) . "</code>\n🌐 <b>STATE:</b> <code>" . val($f['State'] ?? null) . "</code>\n🗺️ <b>REGION:</b> <code>" . val($f['Region'] ?? null) . "</code>\n📦 <b>DIVISION:</b> <code>" . val($f['Division'] ?? null) . "</code>\n⭕ <b>CIRCLE:</b> <code>" . val($f['Circle'] ?? null) . "</code>\n🧱 <b>BLOCK:</b> <code>" . val($f['Block'] ?? null) . "</code>\n🌍 <b>COUNTRY:</b> <code>" . val($f['Country'] ?? null) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n🏣 <b>POST OFFICES (" . count($o) . ")</b>\n━━━━━━━━━━━━━━━━━━━━━━━\n"; foreach ($o as $i => $p) { $msg .= "<b>#" . ($i + 1) . " " . val($p['Name'] ?? null) . "</b>\n🏢 <b>Type:</b> <code>" . val($p['BranchType'] ?? null) . "</code>\n🚚 <b>Delivery:</b> <code>" . val($p['DeliveryStatus'] ?? null) . "</code>\n─────────────────────\n"; } $msg .= "💰 <b>CREDITS REMAINING:</b> <code>$c</code>"; return $msg; }
function formatGstDetail($d, $c) { return "🏢 <b>GST DETAIL INFORMATION</b>\n━━━━━━━━━━━━━━━━━━━━━━━\n🔢 <b>GSTIN:</b> <code>" . val($d['Gstin'] ?? null) . "</code>\n🏷️ <b>TRADE NAME:</b> <code>" . val($d['TradeName'] ?? null) . "</code>\n📋 <b>LEGAL NAME:</b> <code>" . val($d['LegalName'] ?? null) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n📊 <b>TAXPAYER TYPE:</b> <code>" . val($d['TxpType'] ?? null) . "</code>\n🔓 <b>BLOCK STATUS:</b> <code>" . (($d['BlkStatus'] ?? '') === 'U' ? '✅ UNBLOCKED' : '🚫 BLOCKED') . "</code>\n📅 <b>REG DATE:</b> <code>" . val($d['DtReg'] ?? null) . "</code>\n❌ <b>DEREG DATE:</b> <code>" . val($d['DtDReg'] ?? null) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n🏠 <b>ADDRESS</b>\n🏢 <b>Building:</b> <code>" . val($d['AddrBnm'] ?? null) . "</code>\n🔢 <b>Bldg No:</b> <code>" . val($d['AddrBno'] ?? null) . "</code>\n🏬 <b>Floor:</b> <code>" . val($d['AddrFlno'] ?? null) . "</code>\n🛣️ <b>Street:</b> <code>" . val($d['AddrSt'] ?? null) . "</code>\n📍 <b>Location:</b> <code>" . val($d['AddrLoc'] ?? null) . "</code>\n🗺️ <b>State Code:</b> <code>" . val($d['StateCode'] ?? null) . "</code>\n📮 <b>PINCODE:</b> <code>" . val($d['AddrPncd'] ?? null) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n💰 <b>CREDITS REMAINING:</b> <code>$c</code>"; }
function formatAadhaar($dl, $c) { $msg = "🪪 <b>AADHAAR INFORMATION</b>\n━━━━━━━━━━━━━━━━━━━━━━━\n📊 <b>TOTAL RESULTS:</b> <code>" . count($dl) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n"; foreach ($dl as $i => $d) { $msg .= "📋 <b>RESULT #" . ($i + 1) . "</b>\n━━━━━━━━━━━━━━━━━━━━━━━\n👤 <b>NAME:</b> <code>" . val($d['name'] ?? null) . "</code>\n👨‍👦 <b>FATHER NAME:</b> <code>" . val($d['fname'] ?? null) . "</code>\n🆔 <b>AADHAAR ID:</b> <code>" . val($d['id'] ?? null) . "</code>\n📞 <b>MOBILE:</b> <code>" . val($d['mobile'] ?? null) . "</code>\n📡 <b>CIRCLE:</b> <code>" . val($d['circle'] ?? null) . "</code>\n🏠 <b>ADDRESS:</b>\n<code>" . formatAddress($d['address'] ?? '') . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n"; } $msg .= "💰 <b>CREDITS REMAINING:</b> <code>$c</code>"; return $msg; }
function formatChallan($d, $c) { $ch = $d['pending_challans'] ?? []; $msg = "🚨 <b>CHALLAN INFORMATION</b>\n━━━━━━━━━━━━━━━━━━━━━━━\n🔢 <b>REG NO:</b> <code>" . val($d['reg_no'] ?? null) . "</code>\n👤 <b>OWNER:</b> <code>" . val($d['owner_name'] ?? null) . "</code>\n🚘 <b>VEHICLE:</b> <code>" . val($d['vehicle'] ?? null) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n📋 <b>CHALLANS (" . count($ch) . ")</b>\n━━━━━━━━━━━━━━━━━━━━━━━\n"; foreach ($ch as $i => $x) { $off = $x['offence'] ?? null; $ot = is_array($off) ? "• " . implode("\n• ", $off) : val($off); $se = ($x['status'] ?? '') === 'Pending' ? '🟡' : '🟢'; $msg .= "$se <b>CHALLAN #" . ($i + 1) . "</b>\n👤 <b>Violator:</b> <code>" . val($x['violator_name'] ?? null) . "</code>\n🔢 <b>Challan No:</b> <code>" . val($x['challan_no'] ?? null) . "</code>\n📅 <b>Date:</b> <code>" . val($x['date'] ?? null) . "</code>\n💵 <b>Amount:</b> <code>₹" . val($x['amount'] ?? null) . "</code>\n📊 <b>Status:</b> <code>" . val($x['status'] ?? null) . "</code>\n🗺️ <b>State:</b> <code>" . val($x['state'] ?? null) . "</code>\n🚫 <b>Offence:</b> <code>$ot</code>\n─────────────────────\n"; } $msg .= "💰 <b>CREDITS REMAINING:</b> <code>$c</code>"; return $msg; }
function formatIp($d, $c) { return "🌐 <b>IP LOOKUP</b>\n━━━━━━━━━━━━━━━━━━━━━━━\n🔍 <b>IP:</b> <code>" . val($d['query'] ?? null) . "</code>\n🏢 <b>ISP:</b> <code>" . val($d['isp'] ?? null) . "</code>\n🏛️ <b>ORG:</b> <code>" . val($d['org'] ?? null) . "</code>\n📡 <b>AS:</b> <code>" . val($d['as'] ?? null) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n🌍 <b>COUNTRY:</b> <code>" . val($d['country'] ?? null) . "</code>\n🏳️ <b>COUNTRY CODE:</b> <code>" . val($d['countryCode'] ?? null) . "</code>\n🗺️ <b>REGION:</b> <code>" . val($d['regionName'] ?? null) . "</code>\n🔤 <b>REGION CODE:</b> <code>" . val($d['region'] ?? null) . "</code>\n🏙️ <b>CITY:</b> <code>" . val($d['city'] ?? null) . "</code>\n📮 <b>ZIP:</b> <code>" . val($d['zip'] ?? null) . "</code>\n🕒 <b>TIMEZONE:</b> <code>" . val($d['timezone'] ?? null) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n📍 <b>LATITUDE:</b> <code>" . val($d['lat'] ?? null) . "</code>\n📍 <b>LONGITUDE:</b> <code>" . val($d['lon'] ?? null) . "</code>\n━━━━━━━━━━━━━━━━━━━━━━━\n💰 <b>CREDITS REMAINING:</b> <code>$c</code>"; }

function checkForceJoin($userId) {
    global $BOT_TOKEN, $FORCE_CHANNEL;
    if (!$FORCE_CHANNEL) return true;
    $url = "https://api.telegram.org/bot$BOT_TOKEN/getChatMember?chat_id=$FORCE_CHANNEL&user_id=$userId";
    $response = file_get_contents($url);
    if ($response === false) return false;
    $data = json_decode($response, true);
    return isset($data['result']['status']) && in_array($data['result']['status'], ['member', 'administrator', 'creator']);
}

function fetchApi($url) {
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 30);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    return ($httpCode === 200 && $response !== false) ? json_decode($response, true) : null;
}

function generateQrForPlan($userId, $planKey) {
    global $FAM_QR_API, $UPI_ID, $CREDIT_PLANS;
    if (!isset($CREDIT_PLANS[$planKey])) return null;
    $amount = $CREDIT_PLANS[$planKey]['price'];
    $response = fetchApi("$FAM_QR_API?upi=$UPI_ID&amount=$amount");
    if ($response && ($response['status'] ?? '') === 'success') {
        return ['order_id' => $response['data']['order_id'], 'qr_url' => $response['data']['qr_url'], 'expires_at' => $response['data']['expires_at_ist'], 'amount' => $amount, 'plan_key' => $planKey];
    }
    return null;
}

function verifyPayment($orderId) {
    global $FAM_VERIFY_API, $FAM_API_KEY;
    return fetchApi("$FAM_VERIFY_API?order_id=$orderId&api_key=$FAM_API_KEY");
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
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    $response = curl_exec($ch);
    curl_close($ch);
    return json_decode($response, true);
}

function sendPhoto($chatId, $photoUrl, $caption = '', $replyMarkup = null) {
    global $BOT_TOKEN;
    $postData = ['chat_id' => $chatId, 'photo' => $photoUrl, 'caption' => $caption, 'parse_mode' => 'HTML'];
    if ($replyMarkup) $postData['reply_markup'] = json_encode($replyMarkup);
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, "https://api.telegram.org/bot$BOT_TOKEN/sendPhoto");
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $postData);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 10);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    $response = curl_exec($ch);
    curl_close($ch);
    return json_decode($response, true);
}

function editMessageText($chatId, $messageId, $text, $replyMarkup = null) {
    global $BOT_TOKEN;
    $postData = ['chat_id' => $chatId, 'message_id' => $messageId, 'text' => $text, 'parse_mode' => 'HTML'];
    if ($replyMarkup) $postData['reply_markup'] = json_encode($replyMarkup);
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, "https://api.telegram.org/bot$BOT_TOKEN/editMessageText");
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $postData);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 10);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    $response = curl_exec($ch);
    curl_close($ch);
    return json_decode($response, true);
}

function editMessageMedia($chatId, $messageId, $mediaUrl, $caption = '', $replyMarkup = null) {
    global $BOT_TOKEN;
    $postData = [
        'chat_id' => $chatId,
        'message_id' => $messageId,
        'media' => json_encode(['type' => 'photo', 'media' => $mediaUrl, 'caption' => $caption, 'parse_mode' => 'HTML']),
    ];
    if ($replyMarkup) $postData['reply_markup'] = json_encode($replyMarkup);
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, "https://api.telegram.org/bot$BOT_TOKEN/editMessageMedia");
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $postData);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 10);
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
    curl_setopt($ch, CURLOPT_TIMEOUT, 10);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    $response = curl_exec($ch);
    curl_close($ch);
    return json_decode($response, true);
}

function getForceJoinKeyboard() {
    global $FORCE_CHANNEL;
    $cu = str_replace('@', '', $FORCE_CHANNEL);
    return ['inline_keyboard' => [[['text' => '📢 JOIN CHANNEL', 'url' => "https://t.me/$cu"]], [['text' => '✅ CHECK JOIN', 'callback_data' => 'check_join']]]];
}

function getAdminKeyboard() {
    return ['inline_keyboard' => [
        [['text' => '📊 BOT STATISTICS', 'callback_data' => 'admin_stats'], ['text' => '📋 VIEW PENDING PAYMENTS', 'callback_data' => 'admin_view_pending']],
        [['text' => '➕ ADD CREDITS', 'callback_data' => 'admin_add_credit'], ['text' => '🎁 BULK ADD CREDITS', 'callback_data' => 'admin_bulk_credit']],
        [['text' => '➖ REMOVE CREDITS', 'callback_data' => 'admin_remove_credit'], ['text' => '∞ ADD UNLIMITED', 'callback_data' => 'admin_add_unlimited']],
        [['text' => '🚫 REMOVE UNLIMITED', 'callback_data' => 'admin_remove_unlimited'], ['text' => '👥 ALL USERS', 'callback_data' => 'admin_all_users']],
        [['text' => '📜 USER HISTORY', 'callback_data' => 'admin_user_history'], ['text' => '📢 BROADCAST', 'callback_data' => 'admin_broadcast']],
        [['text' => '🚫 BLOCK USER', 'callback_data' => 'admin_block_user'], ['text' => '✅ UNBLOCK USER', 'callback_data' => 'admin_unblock_user']],
        [['text' => '❌ CANCEL', 'callback_data' => 'admin_cancel']]
    ]];
}

function getMainMenuKeyboard() {
    return [
        'inline_keyboard' => [
            [['text' => '📱 MOBILE LOOKUP', 'callback_data' => 'menu_mobile'], ['text' => '🪪 AADHAAR LOOKUP', 'callback_data' => 'menu_aadhaar']],
            [['text' => '👨‍👩‍👧‍👦 FAMILY LOOKUP', 'callback_data' => 'menu_family'], ['text' => '🛢️ LPG LOOKUP', 'callback_data' => 'menu_lpg']],
            [['text' => '🚗 VEHICLE LOOKUP', 'callback_data' => 'menu_vehicle'], ['text' => '📞 VNUM LOOKUP', 'callback_data' => 'menu_vnum']],
            [['text' => '🚨 CHALLAN LOOKUP', 'callback_data' => 'menu_challan'], ['text' => '📸 INSTAGRAM LOOKUP', 'callback_data' => 'menu_instagram']],
            [['text' => '🎮 FREE FIRE LOOKUP', 'callback_data' => 'menu_freefire'], ['text' => '💳 PAYTM LOOKUP', 'callback_data' => 'menu_paytm']],
            [['text' => '💳 PAN LOOKUP', 'callback_data' => 'menu_pan'], ['text' => '🏢 GST LOOKUP', 'callback_data' => 'menu_gst']],
            [['text' => '📇 PAN TO GST', 'callback_data' => 'menu_pangst'], ['text' => '🏦 IFSC LOOKUP', 'callback_data' => 'menu_ifsc']],
            [['text' => '📍 PINCODE LOOKUP', 'callback_data' => 'menu_pincode'], ['text' => '✈️ TELEGRAM LOOKUP', 'callback_data' => 'menu_telegram']],
            [['text' => '🌐 IP LOOKUP', 'callback_data' => 'menu_ip'], ['text' => '👤 PROFILE', 'callback_data' => 'menu_profile']],
            [['text' => '💰 BUY CREDITS', 'callback_data' => 'buy_credits']]
        ]
    ];
}

function getMenuCancelKeyboard() {
    return ['inline_keyboard' => [[['text' => '❌ CANCEL', 'callback_data' => 'menu_cancel']]]];
}

function sendLongMessage($chatId, $text, $replyMarkup = null) {
    $maxLength = 4000;
    if (strlen($text) <= $maxLength) {
        return sendMessage($chatId, $text, $replyMarkup);
    }
    $chunks = str_split($text, $maxLength);
    $lastMsg = null;
    foreach ($chunks as $i => $chunk) {
        if ($i === count($chunks) - 1) {
            $lastMsg = sendMessage($chatId, $chunk, $replyMarkup);
        } else {
            $lastMsg = sendMessage($chatId, $chunk);
        }
        usleep(200000);
    }
    return $lastMsg;
}

function processLookupRequest($chatId, $userId, $lookupType, $term, $noResultMessage) {
    global $API_ENDPOINTS, $API_KEY;
    
    if (!checkForceJoin($userId)) { sendMessage($chatId, "❌ <b>Please join our channel first!</b>", getForceJoinKeyboard()); return; }
    
    $cooldown = checkCooldown($userId);
    if ($cooldown > 0) { sendMessage($chatId, "⏳ Please wait $cooldown seconds before next request!"); return; }
    
    if (!isAdmin($userId) && !hasSufficientCredits($userId)) {
        $user = getUser($userId);
        $credits = $user ? $user['credits'] : '0';
        sendMessage($chatId, "❌ <b>INSUFFICIENT CREDITS</b>\n\n💰 <b>CREDITS REMAINING:</b> <code>$credits</code>\n\nUse /buy to purchase more credits.");
        return;
    }
    
    updateLastRequest($userId);
    
    $apiEndpoint = $API_ENDPOINTS[$lookupType] ?? null;
    if (!$apiEndpoint) { sendMessage($chatId, "❌ Invalid lookup type."); return; }
    
    $apiUrl = str_replace(['{key}', '{term}'], [$API_KEY, urlencode($term)], $apiEndpoint);
    
    $statusMsg = sendMessage($chatId, "⏳ Processing your request...");
    $rawData = fetchApi($apiUrl);
    
    if (!is_valid_response($rawData) || !has_actual_data($rawData)) {
        $user = getUser($userId);
        $credits = $user ? $user['credits'] : '0';
        editMessageText($chatId, $statusMsg['result']['message_id'], "❌ <b>$noResultMessage</b>\n\n💡 <b>No credits were deducted</b>\n\n💰 <b>CREDITS REMAINING:</b> <code>$credits</code>");
        return;
    }
    
    $extractedData = extract_data_for_type($lookupType, $rawData);
    
    $validatorMap = ['mobile' => 'validateMobile', 'aadhaar' => 'validateAadhaar', 'family' => 'validateFamily', 'lpg' => 'validateLpg', 'paytm' => 'validatePaytm', 'instagram' => 'validateInstagram', 'freefire' => 'validateFreefire', 'pan' => 'validatePan', 'pangst' => 'validatePanToGst', 'ifsc' => 'validateIfsc', 'pincode' => 'validatePincode', 'telegram' => 'validateTelegram', 'gst' => 'validateGst', 'vnum' => 'validateVnum', 'challan' => 'validateChallan', 'ip' => 'validateIp', 'vehicle' => 'validateVehicle'];
    
    if (isset($validatorMap[$lookupType])) {
        $validator = $validatorMap[$lookupType];
        if (!$validator($extractedData)) {
            $user = getUser($userId);
            $credits = $user ? $user['credits'] : '0';
            editMessageText($chatId, $statusMsg['result']['message_id'], "❌ <b>$noResultMessage</b>\n\n💡 <b>No credits were deducted</b>\n\n💰 <b>CREDITS REMAINING:</b> <code>$credits</code>");
            return;
        }
    }
    
    if (!isAdmin($userId)) {
        if (!deductCredit($userId)) {
            $user = getUser($userId);
            $credits = $user ? $user['credits'] : '0';
            editMessageText($chatId, $statusMsg['result']['message_id'], "❌ <b>INSUFFICIENT CREDITS</b>\n\n💰 <b>CREDITS REMAINING:</b> <code>$credits</code>");
            return;
        }
    }
    
    $user = getUser($userId);
    $credits = $user ? $user['credits'] : '0';
    
    $formatterMap = ['mobile' => 'formatMobile', 'aadhaar' => 'formatAadhaar', 'family' => 'formatFamily', 'lpg' => 'formatLpg', 'paytm' => 'formatPaytm', 'instagram' => 'formatInstagram', 'freefire' => 'formatFreefire', 'pan' => 'formatPanDetail', 'pangst' => 'formatPanToGst', 'ifsc' => 'formatIfsc', 'pincode' => 'formatPincode', 'telegram' => 'formatTelegram', 'gst' => 'formatGstDetail', 'vnum' => 'formatVnum', 'challan' => 'formatChallan', 'ip' => 'formatIp', 'vehicle' => 'formatVehicle'];
    
    $formatter = $formatterMap[$lookupType];
    $result = $formatter($extractedData, $credits);
    
    $resultCount = is_array($extractedData) ? count($extractedData) : 1;
    addHistory($userId, $lookupType, $term, $resultCount);
    
    deleteMessage($chatId, $statusMsg['result']['message_id']);
    sendLongMessage($chatId, $result);
}

function handleStart($chatId, $userId, $name, $username, $text = '') {
    $referredBy = null;
    if (strpos($text, ' ') !== false) {
        $parts = explode(' ', $text, 2);
        if (isset($parts[1])) {
            $refCode = trim($parts[1]);
            $db = loadDatabase();
            foreach ($db['users'] as $user) {
                if (($user['referral_code'] ?? '') === $refCode && $user['user_id'] !== (string)$userId) { $referredBy = $user['user_id']; break; }
            }
        }
    }
    if (!getUser($userId)) createUser($userId, $name, $username, $referredBy);
    $user = getUser($userId);
    
    $caption = "🌟 ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ 𝐆ᴀᴜʀᴀᴠ 𝐃ᴇᴛᴀɪʟ𝐬 𝐁ᴏᴛ 🌟\n\n🔍 ʟᴏᴏᴋᴜᴘ ᴀɴʏ ᴍᴏʙɪʟᴇ ɴᴜᴍʙᴇʀ\n🪪 ᴛʀᴀᴄᴋ ᴀᴀᴅʜᴀᴀʀ ᴅᴇᴛᴀɪʟꜱ\n👨‍👩‍👧‍👦 ꜰɪɴᴅ ꜰᴀᴍɪʟʏ ᴅᴇᴛᴀɪʟꜱ\n\n✨ ᴜꜱᴇ ᴛʜᴇ ᴍᴇɴᴜ ʙᴇʟᴏᴡ ᴛᴏ ɴᴀᴠɪɢᴀᴛᴇ.\n\n🎁 ʏᴏᴜ ʜᴀᴠᴇ <b>{$user['credits']}</b> ꜰʀᴇᴇ ʟᴏᴏᴋᴜᴘ ᴀᴠᴀɪʟᴀʙʟᴇ!";
    
    sendPhoto($chatId, $GLOBALS['WELCOME_IMAGE'], $caption, getMainMenuKeyboard());
}

function handleProfile($chatId, $userId) {
    $user = getUser($userId);
    if (!$user) { handleStart($chatId, $userId, 'User', 'No Username'); return; }
    $role = isAdmin($userId) ? '👑 Admin' : '👤 User';
    $balance = $user['credits'] === 'UNLIMITED' ? 'Unlimited' : $user['credits'] . ' Credits';
    sendMessage($chatId, "👤 <b>Profile Info:</b>\n━━━━━━━━━━━━━━━━━━\n📛 <b>Name:</b> {$user['name']}\n🆔 <b>User ID:</b> <code>$userId</code>\n👑 <b>Role:</b> $role\n💰 <b>Balance:</b> <b>$balance</b>\n🎁 <b>Referral Code:</b> <code>{$user['referral_code']}</code>\n📅 <b>Joined:</b> {$user['joined_date']}");
}

function handleBuy($chatId) {
    global $CREDIT_PLANS;
    $plansText = "💳 <b>AVAILABLE CREDIT PLANS:</b>\n\n";
    foreach ($CREDIT_PLANS as $pd) $plansText .= "• <b>{$pd['display']}</b>\n";
    $plansText .= "\n📝 <b>Select a plan below to pay with QR:</b>";
    $keyboard = ['inline_keyboard' => []];
    foreach ($CREDIT_PLANS as $pk => $pd) {
        $label = $pk === 'unlimited' ? '₹3200 — UNLIMITED CREDIT' : "₹{$pd['price']} — {$pd['credits']} CREDITS";
        $keyboard['inline_keyboard'][] = [['text' => $label, 'callback_data' => "buy_$pk"]];
    }
    sendMessage($chatId, $plansText, $keyboard);
}

function handleMenuCallback($callbackQuery) {
    $callbackId = $callbackQuery['id'];
    $userId = $callbackQuery['from']['id'];
    $chatId = $callbackQuery['message']['chat']['id'];
    $messageId = $callbackQuery['message']['message_id'];
    $data = $callbackQuery['data'];
    
    if ($data === 'menu_cancel') {
        clearUserState($userId);
        answerCallbackQuery($callbackId, 'Cancelled!');
        deleteMessage($chatId, $messageId);
        sendMessage($chatId, "❌ Action cancelled.");
        return;
    }
    
    if (strpos($data, 'menu_') === 0) {
        $lookupType = substr($data, 5);
        setUserState($userId, 'lookup', $lookupType);
        $typeNames = [
            'mobile' => '📱 Mobile Number',
            'aadhaar' => '🪪 Aadhaar Number',
            'family' => '👨‍👩‍👧‍👦 Aadhaar Number',
            'lpg' => '🛢️ LPG Consumer Number',
            'vehicle' => '🚗 Vehicle Number (e.g. MH01AB1234)',
            'vnum' => '📞 Vehicle Number (e.g. MH01AB1234)',
            'challan' => '🚨 Vehicle Number (e.g. MH01AB1234)',
            'instagram' => '📸 Instagram Username',
            'freefire' => '🎮 Free Fire UID',
            'paytm' => '💳 Paytm Number or VPA',
            'pan' => '💳 PAN Number (e.g. ABCDE1234F)',
            'gst' => '🏢 GST Number (e.g. 22AAAAA0000A1Z5)',
            'pangst' => '📇 PAN Number (e.g. ABCDE1234F)',
            'ifsc' => '🏦 IFSC Code (e.g. SBIN0001234)',
            'pincode' => '📍 Pincode (e.g. 400001)',
            'telegram' => '✈️ Telegram Username',
            'ip' => '🌐 IP Address (e.g. 192.168.1.1)'
        ];
        $typeName = $typeNames[$lookupType] ?? ucfirst($lookupType);
        answerCallbackQuery($callbackId, "Enter $typeName");
        deleteMessage($chatId, $messageId);
        sendMessage($chatId, "📝 <b>Enter $typeName</b>\n\nSend the value to lookup.\n\nType /cancel to cancel.", getMenuCancelKeyboard());
        return;
    }
    
    if ($data === 'menu_profile') {
        answerCallbackQuery($callbackId);
        handleProfile($chatId, $userId);
        return;
    }
}

function handleCallback($callbackQuery) {
    global $CREDIT_PLANS, $SUCCESS_IMAGE, $FAILED_IMAGE, $LOG_CHANNEL;
    $callbackId = $callbackQuery['id'];
    $userId = $callbackQuery['from']['id'];
    $chatId = $callbackQuery['message']['chat']['id'];
    $messageId = $callbackQuery['message']['message_id'];
    $data = $callbackQuery['data'];
    
    if ($data === 'check_join') {
        if (checkForceJoin($userId)) { answerCallbackQuery($callbackId, '✅ Thanks for joining!'); sendMessage($chatId, "✅ Now you can use the bot!\n/start karein bot use karne ke liye."); }
        else answerCallbackQuery($callbackId, '❌ Please join the channel first!', true);
        return;
    }
    
    if (strpos($data, 'menu_') === 0 || $data === 'menu_profile' || $data === 'menu_cancel') {
        handleMenuCallback($callbackQuery);
        return;
    }
    
    if (!isAdmin($userId) && strpos($data, 'buy_') !== 0 && strpos($data, 'verify_') !== 0 && $data !== 'buy_credits' && strpos($data, 'regen_') !== 0 && strpos($data, 'cancelqr_') !== 0) {
        answerCallbackQuery($callbackId, '❌ Aap admin nahi hain!', true);
        return;
    }
    
    if ($data === 'buy_credits') { handleBuy($chatId); answerCallbackQuery($callbackId); return; }
    
    if (strpos($data, 'buy_') === 0) {
        $planKey = substr($data, 4);
        if (!isset($CREDIT_PLANS[$planKey])) { answerCallbackQuery($callbackId, 'Invalid plan!'); return; }
        answerCallbackQuery($callbackId, 'Generating QR code...');
        $qrData = generateQrForPlan($userId, $planKey);
        if (!$qrData) { sendMessage($chatId, '❌ Failed to generate QR code. Please try again.'); return; }
        $plan = $CREDIT_PLANS[$planKey];
        $caption = "💳 <b>QR PAYMENT</b>\n━━━━━━━━━━━━━━━━━━\n📦 <b>Plan:</b> <code>{$plan['display']}</code>\n💰 <b>Amount:</b> <code>₹{$qrData['amount']}</code>\n⏳ <b>Expires:</b> <code>{$qrData['expires_at']}</code>\n\n📲 <i>Scan QR code to pay</i>";
        $keyboard = ['inline_keyboard' => [[['text' => '✅ VERIFY PAYMENT', 'callback_data' => "verify_{$qrData['order_id']}_{$planKey}_$userId"]], [['text' => '❌ CANCEL', 'callback_data' => "cancelqr_$userId"]]]];
        deleteMessage($chatId, $messageId);
        sendPhoto($chatId, $qrData['qr_url'], $caption, $keyboard);
        return;
    }
    
    if (strpos($data, 'cancelqr_') === 0) {
        $targetUserId = substr($data, 9);
        if ((string)$userId !== $targetUserId && !isAdmin($userId)) { answerCallbackQuery($callbackId, 'This is not your payment!'); return; }
        answerCallbackQuery($callbackId, 'Payment cancelled.');
        deleteMessage($chatId, $messageId);
        sendMessage($chatId, "❌ <b>Payment cancelled.</b>\n\nUse /buy to purchase credits.");
        return;
    }
    
    if (strpos($data, 'regen_') === 0) {
        $parts = explode('_', $data);
        $planKey = $parts[1];
        $targetUserId = $parts[2];
        if ((string)$userId !== $targetUserId && !isAdmin($userId)) { answerCallbackQuery($callbackId, 'This is not your payment!'); return; }
        answerCallbackQuery($callbackId, 'Generating new QR code...');
        $qrData = generateQrForPlan($targetUserId, $planKey);
        if (!$qrData) { sendMessage($chatId, '❌ Failed to generate QR code. Please try again.'); return; }
        $plan = $CREDIT_PLANS[$planKey];
        $caption = "💳 <b>QR PAYMENT</b>\n━━━━━━━━━━━━━━━━━━\n📦 <b>Plan:</b> <code>{$plan['display']}</code>\n💰 <b>Amount:</b> <code>₹{$qrData['amount']}</code>\n⏳ <b>Expires:</b> <code>{$qrData['expires_at']}</code>\n\n📲 <i>Scan QR code to pay</i>";
        $keyboard = ['inline_keyboard' => [[['text' => '✅ VERIFY PAYMENT', 'callback_data' => "verify_{$qrData['order_id']}_{$planKey}_$targetUserId"]], [['text' => '❌ CANCEL', 'callback_data' => "cancelqr_$targetUserId"]]]];
        editMessageMedia($chatId, $messageId, $qrData['qr_url'], $caption, $keyboard);
        return;
    }
    
    if (strpos($data, 'verify_') === 0) {
        $parts = explode('_', $data);
        $orderId = $parts[1];
        $planKey = $parts[2];
        $planUserId = $parts[3];
        if ((string)$userId !== $planUserId && !isAdmin($userId)) { answerCallbackQuery($callbackId, 'This is not your payment!'); return; }
        answerCallbackQuery($callbackId, '⏳ Verifying payment... Please wait');
        
        $checkingCaption = "⏳ <b>VERIFYING PAYMENT...</b>\n━━━━━━━━━━━━━━━━━━\n🆔 <b>Order ID:</b> <code>$orderId</code>\n\n<i>Please wait while we verify your payment...</i>";
        editMessageText($chatId, $messageId, $checkingCaption);
        
        $result = verifyPayment($orderId);
        if (!$result || ($result['status'] ?? '') !== 'success') {
            $failedCaption = "❌ <b>Deposit Not Found...</b>\n━━━━━━━━━━━━━━━━━━\n🆔 <b>Order Id:</b> <code>$orderId</code>\n\n<i>Don't Use Same Qr Code Again, Generate New Qr Code</i>";
            $keyboard = ['inline_keyboard' => [[['text' => '👀 REGENERATE QR', 'callback_data' => "regen_{$planKey}_$planUserId"]], [['text' => '❌ CANCEL', 'callback_data' => "cancelqr_$planUserId"]]]];
            editMessageMedia($chatId, $messageId, $FAILED_IMAGE, $failedCaption, $keyboard);
            return;
        }
        $paymentData = $result['data'] ?? [];
        $amount = $paymentData['amount'] ?? 0;
        $txnId = $paymentData['transaction_id'] ?? 'N/A';
        $utr = $paymentData['utr'] ?? 'N/A';
        $senderName = $paymentData['sender_name'] ?? 'N/A';
        $paymentTime = $paymentData['payment_time_ist'] ?? 'N/A';
        if (!isset($CREDIT_PLANS[$planKey])) { sendMessage($chatId, '❌ Invalid plan configuration!'); return; }
        $plan = $CREDIT_PLANS[$planKey];
        
        $db = loadDatabase();
        $alreadyCredited = false;
        if (isset($db['pending_payments'][$orderId])) {
            $alreadyCredited = true;
        } else {
            $db['pending_payments'][$orderId] = [
                'user_id' => $planUserId,
                'plan_key' => $planKey,
                'amount' => $amount,
                'utr' => $utr,
                'txn_id' => $txnId,
                'time' => $paymentTime,
                'status' => 'completed'
            ];
            saveDatabase($db);
            
            if ($planKey === 'unlimited') { setUnlimitedCredits($planUserId); $creditMsg = 'UNLIMITED credits'; }
            else { updateUserCredits($planUserId, $plan['credits']); $creditMsg = $plan['credits'] . ' credits'; }
            updateStats($planKey, $plan['price']);
        }
        
        $user = getUser($planUserId);
        $remainingCredits = $user ? $user['credits'] : '0';
        $successCaption = "✅ <b>PAYMENT SUCCESSFUL!</b>\n━━━━━━━━━━━━━━━━━━\n💰 <b>Amount:</b> ₹$amount\n👤 <b>Name:</b> $senderName\n🔢 <b>UTR:</b> <code>$utr</code>\n🧾 <b>Txn ID:</b> <code>$txnId</code>\n🕒 <b>Time:</b> $paymentTime\n━━━━━━━━━━━━━━━━━━\n🎁 <b>Credits Added:</b> $creditMsg\n💰 <b>Available Credits:</b> <code>$remainingCredits</code>";
        editMessageMedia($chatId, $messageId, $SUCCESS_IMAGE, $successCaption);
        
        $logMsg = "🪙 <b>NEW QR PAYMENT</b>\n━━━━━━━━━━━━━━━━━━\n👤 <b>User:</b> <code>$planUserId</code>\n📦 <b>Plan:</b> {$plan['display']}\n💰 <b>Amount:</b> ₹$amount\n🔢 <b>UTR:</b> <code>$utr</code>\n🕒 <b>Time:</b> $paymentTime";
        sendMessage($LOG_CHANNEL, $logMsg);
        return;
    }
    
    if (strpos($data, 'admin_') === 0) {
        switch ($data) {
            case 'admin_stats':
                $stats = getStats();
                $db = loadDatabase();
                $totalUsers = count($db['users']);
                $bannedUsers = 0; $unlimitedUsers = 0;
                foreach ($db['users'] as $u) { if ($u['banned']) $bannedUsers++; if ($u['credits'] === 'UNLIMITED') $unlimitedUsers++; }
                $statsText = "📊 <b>Bot Statistics</b>\n━━━━━━━━━━━━━━━━━━\n💰 <b>Today's Income:</b> ₹{$stats['today_income']}\n💰 <b>Total Income:</b> ₹{$stats['total_income']}\n━━━━━━━━━━━━━━━━━━\n📈 <b>Plan Purchases Today:</b>";
                if (isset($stats['plan_counts']) && count($stats['plan_counts']) > 0) { foreach ($stats['plan_counts'] as $pk => $cnt) { $pn = $CREDIT_PLANS[$pk]['display'] ?? $pk; $statsText .= "\n• $pn: $cnt"; } }
                else $statsText .= "\n• No purchases today";
                $statsText .= "\n━━━━━━━━━━━━━━━━━━\n👥 <b>User Stats:</b>\n• Total: $totalUsers\n• Banned: $bannedUsers\n• Unlimited: $unlimitedUsers\n• Active: " . ($totalUsers - $bannedUsers);
                sendMessage($chatId, $statsText);
                answerCallbackQuery($callbackId);
                break;
            case 'admin_view_pending':
                $db = loadDatabase();
                $pending = $db['pending_payments'] ?? [];
                $msg = "📋 <b>PENDING PAYMENTS</b>\n━━━━━━━━━━━━━━━━━━\n";
                if (count($pending) > 0) {
                    foreach ($pending as $oid => $p) {
                        $msg .= "🆔 <b>Order:</b> <code>$oid</code>\n👤 <b>User:</b> <code>{$p['user_id']}</code>\n📦 <b>Plan:</b> {$p['plan_key']}\n💰 <b>Amount:</b> ₹{$p['amount']}\n🔢 <b>UTR:</b> <code>{$p['utr']}</code>\n🕒 <b>Time:</b> {$p['time']}\n━━━━━━━━━━━━━━━━━━\n";
                    }
                } else {
                    $msg .= "• No pending payments";
                }
                sendMessage($chatId, $msg);
                answerCallbackQuery($callbackId);
                break;
            case 'admin_all_users':
                $db = loadDatabase();
                $users = $db['users'];
                $msg = "👥 <b>ALL USERS</b>\n━━━━━━━━━━━━━━━━━━\n";
                $count = 0;
                foreach ($users as $u) {
                    $count++;
                    $msg .= "👤 <b>User #$count</b>\n🆔 <b>ID:</b> <code>{$u['user_id']}</code>\n📛 <b>Name:</b> {$u['name']}\n💰 <b>Credits:</b> {$u['credits']}\n🚫 <b>Banned:</b> " . ($u['banned'] ? 'YES' : 'NO') . "\n━━━━━━━━━━━━━━━━━━\n";
                    if ($count >= 50) { $msg .= "\n⚠️ <i>Showing first 50 users</i>"; break; }
                }
                if ($count == 0) $msg .= "• No users found";
                sendMessage($chatId, $msg);
                answerCallbackQuery($callbackId);
                break;
            case 'admin_user_history':
                setUserState($userId, 'viewhistory');
                sendMessage($chatId, "📜 <b>User History</b>\nSend user ID to view their history.");
                answerCallbackQuery($callbackId);
                break;
            case 'admin_add_credit': setUserState($userId, 'addcredit'); sendMessage($chatId, "💰 <b>Add Credit</b>\nSend: <code>user_id amount</code>"); answerCallbackQuery($callbackId); break;
            case 'admin_bulk_credit': setUserState($userId, 'bulkcredit'); sendMessage($chatId, "🎁 <b>Bulk Add Credits</b>\nSend amount to add to ALL users."); answerCallbackQuery($callbackId); break;
            case 'admin_remove_credit': setUserState($userId, 'removecredit'); sendMessage($chatId, "📉 <b>Remove Credit</b>\nSend: <code>user_id amount</code>"); answerCallbackQuery($callbackId); break;
            case 'admin_add_unlimited': setUserState($userId, 'addunlimited'); sendMessage($chatId, "∞ <b>Add Unlimited</b>\nSend user ID."); answerCallbackQuery($callbackId); break;
            case 'admin_remove_unlimited': setUserState($userId, 'removeunlimited'); sendMessage($chatId, "🚫 <b>Remove Unlimited</b>\nSend user ID."); answerCallbackQuery($callbackId); break;
            case 'admin_broadcast': setUserState($userId, 'broadcast'); sendMessage($chatId, "📢 <b>Broadcast</b>\nSend message to broadcast to all users."); answerCallbackQuery($callbackId); break;
            case 'admin_block_user': setUserState($userId, 'ban'); sendMessage($chatId, "🚫 <b>Block User</b>\nSend user ID."); answerCallbackQuery($callbackId); break;
            case 'admin_unblock_user': setUserState($userId, 'unban'); sendMessage($chatId, "✅ <b>Unblock User</b>\nSend user ID."); answerCallbackQuery($callbackId); break;
            case 'admin_cancel': clearUserState($userId); sendMessage($chatId, "❌ Action cancelled."); answerCallbackQuery($callbackId); break;
        }
    }
}

function handleCommand($message) {
    $chatId = $message['chat']['id'];
    $userId = $message['from']['id'];
    $name = $message['from']['first_name'] ?? 'User';
    $username = $message['from']['username'] ?? 'No Username';
    $text = $message['text'] ?? '';
    $parts = explode(' ', $text);
    $command = strtolower($parts[0]);
    $args = array_slice($parts, 1);
    
    switch ($command) {
        case '/start': handleStart($chatId, $userId, $name, $username, $text); break;
        case '/profile': handleProfile($chatId, $userId); break;
        case '/buy': handleBuy($chatId); break;
        case '/admin':
            if (!isAdmin($userId)) { sendMessage($chatId, "❌ Aap admin nahi hain!"); return; }
            sendMessage($chatId, "👑 <b>Admin Panel</b> 👑\n━━━━━━━━━━━━━━━━━━\n\nNiche diye gaye buttons ka use karke bot manage karein.", getAdminKeyboard());
            break;
        case '/cancel':
            clearUserState($userId);
            sendMessage($chatId, "❌ Action cancelled.");
            break;
        default:
            $state = getUserState($userId);
            if ($state) handleStateMessage($chatId, $userId, $state, $text);
            break;
    }
}

function handleStateMessage($chatId, $userId, $state, $text) {
    $action = $state['action'];
    if ($text === '/cancel') { clearUserState($userId); sendMessage($chatId, "❌ Action cancelled."); return; }
    switch ($action) {
        case 'lookup':
            $lookupType = $state['data'];
            clearUserState($userId);
            $typeNames = [
                'mobile' => 'NUMBER',
                'aadhaar' => 'AADHAR NUMBER',
                'family' => 'AADHAR NUMBER',
                'lpg' => 'LPG CONSUMER NUMBER',
                'vehicle' => 'VEHICLE NUMBER',
                'vnum' => 'VEHICLE NUMBER',
                'challan' => 'VEHICLE NUMBER',
                'instagram' => 'INSTAGRAM USERNAME',
                'freefire' => 'FREE FIRE UID',
                'paytm' => 'PAYTM NUMBER OR VPA',
                'pan' => 'PAN NUMBER',
                'gst' => 'GST NUMBER',
                'pangst' => 'PAN NUMBER',
                'ifsc' => 'IFSC CODE',
                'pincode' => 'PINCODE',
                'telegram' => 'TELEGRAM USERNAME',
                'ip' => 'IP ADDRESS'
            ];
            $typeName = $typeNames[$lookupType] ?? strtoupper($lookupType);
            $noResultMessages = [
                'mobile' => "NO INFORMATION FOUND FOR THIS NUMBER",
                'aadhaar' => "NO INFORMATION FOUND FOR THIS AADHAR NUMBER",
                'family' => "NO INFORMATION FOUND FOR THIS AADHAR NUMBER",
                'lpg' => "NO INFORMATION FOUND FOR THIS LPG CONSUMER NUMBER",
                'vehicle' => "NO INFORMATION FOUND FOR THIS VEHICLE NUMBER",
                'vnum' => "NO INFORMATION FOUND FOR THIS VEHICLE NUMBER",
                'challan' => "NO INFORMATION FOUND FOR THIS VEHICLE NUMBER",
                'instagram' => "NO INFORMATION FOUND FOR THIS INSTAGRAM USERNAME",
                'freefire' => "NO INFORMATION FOUND FOR THIS FREE FIRE UID",
                'paytm' => "NO INFORMATION FOUND FOR THIS PAYTM NUMBER",
                'pan' => "NO INFORMATION FOUND FOR THIS PAN NUMBER",
                'gst' => "NO INFORMATION FOUND FOR THIS GST NUMBER",
                'pangst' => "NO INFORMATION FOUND FOR THIS PAN NUMBER",
                'ifsc' => "NO INFORMATION FOUND FOR THIS IFSC CODE",
                'pincode' => "NO INFORMATION FOUND FOR THIS PINCODE",
                'telegram' => "NO INFORMATION FOUND FOR THIS TELEGRAM USERNAME",
                'ip' => "NO INFORMATION FOUND FOR THIS IP ADDRESS"
            ];
            $noResultMsg = $noResultMessages[$lookupType] ?? "NO INFORMATION FOUND";
            processLookupRequest($chatId, $userId, $lookupType, $text, $noResultMsg);
            break;
        case 'viewhistory':
            $db = loadDatabase();
            $targetId = trim($text);
            $history = [];
            foreach ($db['history'] as $h) {
                if ($h['user_id'] === $targetId) $history[] = $h;
            }
            if (count($history) > 0) {
                $msg = "📜 <b>HISTORY FOR USER $targetId</b>\n━━━━━━━━━━━━━━━━━━\n";
                $count = 0;
                foreach (array_reverse($history) as $h) {
                    $count++;
                    $msg .= "🕒 <b>#{$count}</b>\n🔍 <b>Action:</b> {$h['action']}\n📝 <b>Query:</b> {$h['query']}\n📊 <b>Results:</b> {$h['result_count']}\n📅 <b>Time:</b> {$h['timestamp']}\n━━━━━━━━━━━━━━━━━━\n";
                    if ($count >= 20) break;
                }
            } else {
                $msg = "❌ No history found for user $targetId";
            }
            sendMessage($chatId, $msg);
            clearUserState($userId);
            break;
        case 'addcredit':
            $parts = explode(' ', $text);
            if (count($parts) >= 2) {
                $targetId = $parts[0]; 
                $amount = strtoupper($parts[1]);
                if ($amount === 'UNLIMITED') { 
                    setUnlimitedCredits($targetId); 
                    sendMessage($chatId, "✅ Added UNLIMITED credits to $targetId");
                    sendMessage($targetId, "🎖️ <b>UNLIMITED ACCESS GRANTED!</b>\n\n👑 Admin has granted you UNLIMITED credits!\n\nUse /profile to check your status.");
                } else { 
                    $amountInt = (int)$amount;
                    updateUserCredits($targetId, $amountInt); 
                    sendMessage($chatId, "✅ Added $amount credits to $targetId");
                    $targetUser = getUser($targetId);
                    $newBalance = $targetUser ? $targetUser['credits'] : 'N/A';
                    sendMessage($targetId, "🎁 <b>CREDITS ADDED!</b>\n\n💰 <b>Added:</b> $amountInt credits\n💎 <b>New Balance:</b> <code>$newBalance</code>\n\nUse /profile to check your status.");
                }
            } else sendMessage($chatId, "❌ Format: <code>user_id amount</code>");
            clearUserState($userId);
            break;
        case 'bulkcredit':
            $amount = (int)trim($text);
            if ($amount > 0) {
                $db = loadDatabase(); 
                $count = 0;
                $notifiedUsers = [];
                foreach ($db['users'] as $key => $u) {
                    if ($u['credits'] !== 'UNLIMITED') { 
                        $current = is_numeric($u['credits']) ? (int)$u['credits'] : 0; 
                        $db['users'][$key]['credits'] = (string)($current + $amount); 
                        $count++;
                        $notifiedUsers[] = $key;
                    }
                }
                saveDatabase($db);
                sendMessage($chatId, "✅ Added $amount credits to $count users.");
                foreach ($notifiedUsers as $notifiedUserId) {
                    $notifiedUser = $db['users'][$notifiedUserId];
                    if ($notifiedUser) {
                        sendMessage($notifiedUserId, "🎁 <b>BONUS CREDITS ADDED!</b>\n\n💰 <b>Added:</b> $amount credits\n💎 <b>New Balance:</b> <code>{$notifiedUser['credits']}</code>\n\nUse /profile to check your status.");
                    }
                }
            } else sendMessage($chatId, "❌ Invalid amount.");
            clearUserState($userId);
            break;
        case 'removecredit':
            $parts = explode(' ', $text);
            if (count($parts) >= 2) {
                $targetId = $parts[0]; 
                $amount = (int)$parts[1];
                $user = getUser($targetId);
                if ($user) {
                    if ($user['credits'] !== 'UNLIMITED') { 
                        $new = max(0, (int)$user['credits'] - $amount); 
                        $db = loadDatabase(); 
                        $db['users'][(string)$targetId]['credits'] = (string)$new; 
                        saveDatabase($db); 
                        sendMessage($chatId, "✅ Removed $amount credits. New balance: $new");
                        sendMessage($targetId, "⚠️ <b>CREDITS REMOVED!</b>\n\n💰 <b>Removed:</b> $amount credits\n💎 <b>New Balance:</b> <code>$new</code>\n\nUse /profile to check your status.");
                    } else sendMessage($chatId, "User has unlimited credits.");
                } else sendMessage($chatId, "User not found.");
            } else sendMessage($chatId, "❌ Format: <code>user_id amount</code>");
            clearUserState($userId);
            break;
        case 'addunlimited': 
            $targetUserId = trim($text);
            setUnlimitedCredits($targetUserId); 
            sendMessage($chatId, "✅ Set unlimited credits for " . $targetUserId);
            sendMessage($targetUserId, "🎖️ <b>UNLIMITED ACCESS GRANTED!</b>\n\n👑 Admin has granted you UNLIMITED credits!\n\nUse /profile to check your status.");
            clearUserState($userId); 
            break;
        case 'removeunlimited': 
            $targetUserId = trim($text);
            removeUnlimitedCredits($targetUserId); 
            sendMessage($chatId, "✅ Removed unlimited credits from " . $targetUserId);
            sendMessage($targetUserId, "⚠️ <b>UNLIMITED ACCESS REMOVED!</b>\n\nYour unlimited credits have been removed by admin.\n\nUse /profile to check your status.");
            clearUserState($userId); 
            break;
        case 'ban':
            $db = loadDatabase();
            if (isset($db['users'][(string)trim($text)])) { $db['users'][(string)trim($text)]['banned'] = 1; saveDatabase($db); sendMessage($chatId, "✅ User " . trim($text) . " banned."); }
            else sendMessage($chatId, "User not found.");
            clearUserState($userId);
            break;
        case 'unban':
            $db = loadDatabase();
            if (isset($db['users'][(string)trim($text)])) { $db['users'][(string)trim($text)]['banned'] = 0; saveDatabase($db); sendMessage($chatId, "✅ User " . trim($text) . " unbanned."); }
            else sendMessage($chatId, "User not found.");
            clearUserState($userId);
            break;
        case 'broadcast':
            $db = loadDatabase(); $success = 0;
            foreach ($db['users'] as $u) { sendMessage($u['user_id'], $text); $success++; }
            sendMessage($chatId, "✅ Broadcast sent to $success/" . count($db['users']) . " users.");
            clearUserState($userId);
            break;
    }
}

$input = file_get_contents('php://input');
$update = json_decode($input, true);

if (isset($update['message'])) handleCommand($update['message']);
elseif (isset($update['callback_query'])) handleCallback($update['callback_query']);

header('Content-Type: application/json');
echo json_encode(['ok' => true]);
?>
