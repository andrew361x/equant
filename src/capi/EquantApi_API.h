#ifndef EQUANTAPI_API_H
#define EQUANTAPI_API_H

#include "EquantApi_Type.h"
#include <functional>
#ifdef LIB_TRADER_API_EXPORT
#define TRADER_API_EXPORT __declspec(dllexport)
#else
#define TRADER_API_EXPORT __declspec(dllimport)
#endif

//�ص�����ָ�붨��
typedef EEquRetType(*EEqu_SrvFunc)(EEquServiceInfo* service);
//typedef std::function<EEquRetType(EEquServiceInfo* service)> *EEqu_SrvFunc;

extern "C"
{
/**
*  @brief ע���¼��ص�����
*
*  @param func �ص�����ָ��
*  @return 0: ע��ɹ���<0: ע��ʧ�ܻ����Ѿ�ע��
*
*  @details ע���¼��ص�����
*/
TRADER_API_EXPORT EEquRetType E_RegEvent(EEqu_SrvFunc func);

/**
*  @brief ע���¼��ص�����
*
*  @param func �ص�����ָ��
*  @return 0: ע���ɹ���<0: ע��ʧ�ܻ����ظ�ע��
*
*  @details ע���¼��ص�����
*/
TRADER_API_EXPORT EEquRetType E_UnregEvent(EEqu_SrvFunc func);

////////////////////////////////////ϵͳ�����ӿ�///////////////////////////

/**
*  @brief ϵͳ��ʼ���ӿ�
*
*  @return 0: ��ʼ���ɹ���<0: ��ʼ��ʧ��
*
*  @details 
*/
TRADER_API_EXPORT EEquRetType E_Init();

/**
*  @brief ϵͳ��ʼ���ӿ�
*
*  @return 0: �ɹ���<0:ʧ�� 
*
*  @details
*/
TRADER_API_EXPORT EEquRetType E_DeInit();

/**
*  @brief ��������
*
*  @return 0: ���ͳɹ���<0: ����ʧ��
*
*  @details
*/
TRADER_API_EXPORT EEquRetType E_ReqQryExchangeInfo(EEquSessionIdType* SessionId, EEquExchangeReq* req);

/**
*  @brief ����Ʒ����Ϣ
*
*  @return 0: ���ͳɹ���<0: ����ʧ��
*
*  @details
*/
TRADER_API_EXPORT EEquRetType E_ReqQryCommodityInfo(EEquSessionIdType* SessionId, EEquCommodityReq* req);

/**
*  @brief �����Լ��Ϣ
*
*  @return 0: ���ͳɹ���<0: ����ʧ��
*
*  @details
*/
TRADER_API_EXPORT EEquRetType E_ReqQryContractInfo(EEquSessionIdType* SessionId, EEquContractReq* req);

/**
*  @brief ��ʱ��ģ��
*
*  @return 0: ���ͳɹ���<0: ����ʧ��
*
*  @details
*/
TRADER_API_EXPORT EEquRetType E_ReqQryTimeBucketInfo(EEquSessionIdType* SessionId, EEquCommodityTimeBucketReq* req);

/**
*  @brief ���ļ�ʱ����
*
*  @param req :��Լ
*  @return 0: ���ͳɹ���<0: ����ʧ��
*
*  @details
*/
TRADER_API_EXPORT EEquRetType E_ReqSubQuote(EEquSessionIdType* SessionId, EEquContractNoType req[],U32 uLen);

/**
*  @brief �˶���ʱ����
*
*  @param req :��Լ��"" �˶�ȫ����
*  @return 0: ���ͳɹ���<0: ����ʧ��
*
*  @details
*/
TRADER_API_EXPORT EEquRetType E_ReqUnSubQuote(EEquSessionIdType* SessionId, EEquContractNoType* req, U32 uLen);

/**
*  @brief ������ʷ����
*
*  @param  
*  @return 0: ���ͳɹ���<0: ����ʧ��
*
*  @details
*/
TRADER_API_EXPORT EEquRetType E_ReqSubHisQuote(EEquSessionIdType* SessionId, EEquKLineReq* req);

/**
*  @brief �˶���ʷ����
*
*  @param
*  @return 0: ���ͳɹ���<0: ����ʧ��
*
*  @details
*/
TRADER_API_EXPORT EEquRetType E_ReqUnSubHisQuote(EEquSessionIdType* SessionId, EEquContractNoType req);

/**
*  @brief ��ȡ��½�˺�
*
*  @param
*  @return 0: ���ͳɹ���<0: ����ʧ��
*
*  @details
*/
TRADER_API_EXPORT EEquRetType E_ReqQryLoginInfo(EEquSessionIdType* SessionId, EEquLoginInfoReq* req);

/**
*  @brief ��ȡ�ʽ��˺�
*
*  @param
*  @return 0: ���ͳɹ���<0: ����ʧ��
*
*  @details
*/
TRADER_API_EXPORT EEquRetType E_ReqQryUserInfo(EEquSessionIdType* SessionId, EEquUserInfoReq* req);

/**
*  @brief ��ȡ�ʽ���Ϣ
*
*  @param
*  @return 0: ���ͳɹ���<0: ����ʧ��
*
*  @details
*/
TRADER_API_EXPORT EEquRetType E_ReqQryMoney(EEquSessionIdType* SessionId, EEquUserMoneyReq* req);

/**
*  @brief ��ȡί�ж���
*
*  @param
*  @return 0: ���ͳɹ���<0: ����ʧ��
*
*  @details
*/
TRADER_API_EXPORT EEquRetType E_ReqQryOrder(EEquSessionIdType* SessionId, EEquOrderQryReq* req);

/**
*  @brief ��ȡ�ɽ���
*
*  @param
*  @return 0: ���ͳɹ���<0: ����ʧ��
*
*  @details
*/
TRADER_API_EXPORT EEquRetType E_ReqQryMatch(EEquSessionIdType* SessionId, EEquMatchQryReq* req);

/**
*  @brief ��ȡ�ֲ���Ϣ
*
*  @param
*  @return 0: ���ͳɹ���<0: ����ʧ��
*
*  @details
*/
TRADER_API_EXPORT EEquRetType E_ReqQryPosition(EEquSessionIdType* SessionId, EEquPositionQryReq* req);

/**
*  @brief ί���µ�
*
*  @param
*  @return 0: ���ͳɹ���<0: ����ʧ��
*
*  @details
*/
TRADER_API_EXPORT EEquRetType E_ReqInsertOrder(EEquSessionIdType* SessionId, EEquOrderInsertReq* req);

/**
*  @brief ί�г���
*
*  @param
*  @return 0: ���ͳɹ���<0: ����ʧ��
*
*  @details
*/
TRADER_API_EXPORT EEquRetType E_ReqCancelOrder(EEquSessionIdType* SessionId, EEquOrderCancelReq* req);

/**
*  @brief ί�иĵ�
*
*  @param
*  @return 0: ���ͳɹ���<0: ����ʧ��
*
*  @details
*/
TRADER_API_EXPORT EEquRetType E_ReqModifyOrder(EEquSessionIdType* SessionId, EEquOrderModifyReq* req);


/**
*  @brief �л�ͼ����ʾ����
*
*  @param
*  @return 0: ���ͳɹ���<0: ����ʧ��
*
*  @details
*/
TRADER_API_EXPORT EEquRetType E_KLineStrategySwitch(EEquSessionIdType* SessionId, EEquKLineStrategySwitch* data);

/**
*  @brief ���ͻز���ʷ����
*
*  @param
*  @return 0: ���ͳɹ���<0: ����ʧ��
*
*  @details
*/
TRADER_API_EXPORT EEquRetType E_KLineDataResult(EEquSessionIdType* SessionId, EEquKLineDataResult* data);
/**
*  @brief ���»ز���ʷ����
*
*  @param
*  @return 0: ���ͳɹ���<0: ����ʧ��
*
*  @details
*/
TRADER_API_EXPORT EEquRetType E_KLineDataResultNotice(EEquSessionIdType* SessionId, EEquKLineDataResult* data);

/**
*  @brief ����ָ������Ϣ
*
*  @param
*  @return 0: ���ͳɹ���<0: ����ʧ��
*
*  @details
*/
TRADER_API_EXPORT EEquRetType E_AddKLineSeriesInfo(EEquSessionIdType* SessionId, EEquKLineSeriesInfo* data);

/**
*  @brief ���ͻز�ָ������
*
*  @param
*  @return 0: ���ͳɹ���<0: ����ʧ��
*
*  @details
*/
TRADER_API_EXPORT EEquRetType E_KLineSeriesResult(EEquSessionIdType* SessionId, EEquKLineSeriesResult* data);
/**
*  @brief ����ָ������
*
*  @param
*  @return 0: ���ͳɹ���<0: ����ʧ��
*
*  @details
*/
TRADER_API_EXPORT EEquRetType E_KLineSeriesResultNotice(EEquSessionIdType* SessionId, EEquKLineSeriesResult* data);

/**
*  @brief �����ź�����Ϣ
*
*  @param
*  @return 0: ���ͳɹ���<0: ����ʧ��
*
*  @details
*/
TRADER_API_EXPORT EEquRetType E_AddKLineSignalInfo(EEquSessionIdType* SessionId, EEquKLineSignalInfo* data);

/**
*  @brief ���ͻز��ź�����
*
*  @param
*  @return 0: ���ͳɹ���<0: ����ʧ��
*
*  @details
*/
TRADER_API_EXPORT EEquRetType E_KLineSignalResult(EEquSessionIdType* SessionId, EEquKLineSignalResult* data);
/**
*  @brief �����ź�����
*
*  @param
*  @return 0: ���ͳɹ���<0: ����ʧ��
*
*  @details
*/
TRADER_API_EXPORT EEquRetType E_KLineSignalResultNotice(EEquSessionIdType* SessionId, EEquKLineSignalResult* data);
/**
*  @brief ˢ��ָ�ꡢ�ź�֪ͨ
*
*  @param
*  @return 0: ���ͳɹ���<0: ����ʧ��
*
*  @details
*/
TRADER_API_EXPORT EEquRetType E_StrategyDataUpdateNotice(EEquSessionIdType* SessionId, EEquStrategyDataUpdateNotice* data);
/**
*  @brief ����״̬����
*
*  @param
*  @return 0: ���ͳɹ���<0: ����ʧ��
*
*  @details
*/
TRADER_API_EXPORT EEquRetType E_KLineStrategyStateNotice(EEquSessionIdType* SessionId, EEquKlineStrategyStateNotice* data);
/**
*  @brief ������״̬��ѯ
*
*  @param
*  @return 0: ���ͳɹ���<0: ����ʧ��
*
*  @details
*/
TRADER_API_EXPORT EEquRetType E_ReqExchangeStateQry(EEquSessionIdType* SessionId, EEquExchangeStateReq* data);

/**
*  @brief ����ԭʼ��Լ��ѯ
*
*  @param
*  @return 0: ���ͳɹ���<0: ����ʧ��
*
*  @details
*/
TRADER_API_EXPORT EEquRetType E_ReqQrySpreadMapping(EEquSessionIdType* SessionId, EEquSpreadMappingReq* data);

/**
*  @brief �����ѯ
*
*  @param
*  @return 0: ���ͳɹ���<0: ����ʧ��
*
*  @details
*/
TRADER_API_EXPORT EEquRetType E_ReqQryUnderlayMapping(EEquSessionIdType* SessionId, EEquUnderlayMappingReq* data);
}

#endif
