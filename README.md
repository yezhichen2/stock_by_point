UUU Live接入文档
整体接入流程说明
1.商户入驻
商户提供 商户名称、邮箱、手机号

2.平台审核
审核通过，分配APPID和秘钥，商户需要妥善保管

3.商户接入UUU Live平台
商户技术人员根据约定的接口规范接入UUU Live平台，主要包括创建订单接口。 
另外，订单完成后UUU Live将通过数据回调接口，通知商户，需要商户提供回调接口URL。

接口说明
创建订单
商户向平台发起创建订单，如果平台创建订单成功，将返回订单充值/付款URL地址， 
以及必要订单的信息（如：订单编号，支付类型，金额，付款用户ID，下单时间）

平台创建订单成功后，商户把订单充值/付款URL进行跳转，为付款用户打开UUU Live平台收银台界面

请求URL (method=POST) 
https://api.uuulive.com/merchant/integration/create_order
请求参数 （form-data）
参数名	类型	备注
app_id	integer	申请商户获得的APPID标识
user_id	integer	充值／付款用户ID
payment_type	integer	支付方式, 1：银行卡 2：微信 3：支付宝
cash	integer	付款金额
timestamp	integer	秒级别时间戳，用于验证时间有效性
_sign	string	数字签名，签名算法见备注
请求响应 （application/json;charset=UTF-8）
参数名	类型	备注
data	object	＃　请求成功时，存在data对象
data.pay_address	string	充值／付款跳转链接地址
data.order_code	string	订单编号
data.user_id	integer	充值／付款用户ID
data.order_code	string	订单编号
data.payment_type	integer	支付方式
data.cash	integer	付款金额
data.create_at	integer	下单时间(单位秒)
error	object	＃　请求失败时，存在error对象
error.code	integer	错误码
error.name	string	错误标题名称
error.description	string	错误提示消息
注：只要存在error,都视为创建订单失败

订单完成时回调
当订单在UUU Live平台处理完成后，将通过数据回调接口，通知商户，需要商户提供回调接口URL。 
回调接口由UUU Live平台发起,然后等待回调结果, 如果 data.success==true,则说明回调成功。 
其它任意情况，视为回调失败，UUU Live会在5分钟后再次发起回调，重试4小时仍然无法完成，将结束重试。

请求URL (method=POST) 
商户提供回调接口URL
请求参数 （form-data）
参数名	类型	备注
user_id	integer	充值／付款用户ID
order_code	string	订单编号
payment_type	integer	支付方式, 1：银行卡 2：微信 3：支付宝
cash	integer	付款金额(实付)
completed_at	integer	订单完成／结束时间（单位秒）
timestamp	integer	秒级别时间戳，用于验证时间有效性
_sign	string	数字签名，签名算法见备注
请求响应 （application/json;charset=UTF-8）
参数名	类型	备注
data	object	
data.success	bool	回调是否成功收到 data.success=true
接口签名
后端在写对外的API接口时，采用对参数进行签名来保证接口的安全性， 
在设计签名算法的时候，主要考虑的是这几个问题： 
1. 请求的来源是否合法 
2. 请求参数是否被篡改 
3. 请求的唯一性

签名算法
对所有参数的key进行升序排序,然后按顺序取key的值进行拼接字符串String val = key+"="+value+"&"。再使用val =val +"key="+appKey 其中appKey 是密钥，然后对val进行UTF-8转码再进行md5加密。

/**
 * 签名算法
 *
 * @param params 请求参数
 * @param appKey app秘钥
 * @return
 */
public static String sign(Map<String, String> params, String appKey) {
    List<String> keys = Ordering.usingToString().sortedCopy(params.keySet());
    StringBuilder sb = new StringBuilder();
    keys.forEach(key -> sb.append(key).append("=").append(params.get(key)).append("&"));
    sb.append("key").append("=").append(appKey);
    return Hashing.md5().hashString(sb, Charsets.UTF_8).toString();
}
校验签名
/**
 * 校验签名方法
 * @param reqMap 包含请求参数的map
 * @param appKey app秘钥
 * @return
 */
public static boolean verify(Map<String, String> reqMap, String appKey) {
    if (Objects.nonNull(reqMap) && Objects.nonNull(appKey) && reqMap.containsKey("_sign")) {
        String key = reqMap.remove("_sign");
        String currentKey = sign(reqMap, appKey);  // use sign method
        return Objects.equals(key, currentKey);
    }
    return false;
}
测试你的算法
假设你的 AppID=1， AppKey=abcdefg0123456 
假设接口传参为

app_id=1,  //AppID
user_id=1,
payment_type=1,
cash=500,
timestamp=1584602535
参数进行升序，拼接的字符串为

app_id=1&cash=500&payment_type=1&timestamp=1584602535&user_id=1&key=abcdefg0123456
MD5加密后的结果_sign为

51a973e23ead65645099e807251f5f2a
