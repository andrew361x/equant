#ifndef EQUANTAPI_TYPE_H
#define EQUANTAPI_TYPE_H

#pragma pack(push, 1)

//++++++++++++++++++++++++������������++++++++++++++++++++++++++++
//��������
typedef signed char					B8;

//�з�������
typedef signed char					I8;
typedef signed short				I16;
typedef signed int					I32;
typedef signed long long			I64;

//�޷�������
typedef unsigned char				U8;
typedef unsigned short				U16;
typedef unsigned int				U32;
typedef unsigned long long			U64;

//������
typedef float						F32;
typedef double						F64;

//�ַ�����
typedef  char						C8;
typedef  wchar_t				    C16;

//ָ������
typedef void*						PTR;

//�ַ�������
typedef C8							STR10[11];
typedef C8							STR20[21];
typedef C8							STR30[31];
typedef C8							STR40[41];
typedef C8							STR50[51];
typedef C8							STR100[101];
typedef C8							STR200[201];

typedef I32                         EEquRetType;				//����ֵ����

typedef U8                          EEquSrvSrcType;				//��������
static const EEquSrvSrcType			EEQU_SRVSRC_QUOTE = 'Q';	//�������
static const EEquSrvSrcType			EEQU_SRVSRC_HISQUOTE = 'H';	//��ʷ�������
static const EEquSrvSrcType			EEQU_SRVSRC_TRADE = 'T';	//���׷���
static const EEquSrvSrcType			EEQU_SRVSRC_SERVICE = 'S';	//9.5�����

typedef U8                          EEquSrvEventType;			  		//�����¼�����
static const EEquSrvEventType		EEQU_SRVEVENT_CONNECT = 0x01;		//����	Q H T S
static const EEquSrvEventType		EEQU_SRVEVENT_DISCONNECT = 0x02;	//�Ͽ�

static const EEquSrvEventType		EEQU_SRVEVENT_QUOTELOGIN = 0x20;	//��¼����ǰ��
static const EEquSrvEventType		EEQU_SRVEVENT_QINITCOMPLETED = 0x21;//�����ʼ�����
static const EEquSrvEventType		EEQU_SRVEVENT_QUOTESNAP = 0x22;		//��ʱ����--
static const EEquSrvEventType		EEQU_SRVEVENT_EXCHANGE = 0x23;		//������
static const EEquSrvEventType		EEQU_SRVEVENT_COMMODITY = 0x24;		//Ʒ��
static const EEquSrvEventType		EEQU_SRVEVENT_CONTRACT = 0x25;		//��Լ
static const EEquSrvEventType		EEQU_SRVEVENT_QUOTESNAPLV2 = 0x26;	//�������--
static const EEquSrvEventType		EEQU_SRVEVENT_SPRAEDMAPPING = 0x27;	//������Լӳ���ϵ
static const EEquSrvEventType		EEQU_SRVEVENT_UNDERLAYMAPPING = 0x28;//�����Լӳ���ϵ

static const EEquSrvEventType		EEQU_SRVEVENT_HISLOGIN = 0x40;		//��¼��ʷ����
static const EEquSrvEventType		EEQU_SRVEVENT_HINITCOMPLETED = 0x41;//��ʷ��ʼ�����
static const EEquSrvEventType		EEQU_SRVEVENT_HISQUOTEDATA = 0x42;	//��ʷ�������ݲ�ѯӦ��
static const EEquSrvEventType		EEQU_SRVEVENT_HISQUOTENOTICE = 0x43;//��ʷ�������ݱ仯֪ͨ
static const EEquSrvEventType		EEQU_SRVEVENT_TIMEBUCKET = 0x44;	//ʱ��ģ��

static const EEquSrvEventType       EEQU_SRVEVENT_TRADE_LOGINQRY = 0x60; //��½�˺Ų�ѯ
static const EEquSrvEventType       EEQU_SRVEVENT_TRADE_LOGINNOTICE = 0x61; //��½�˺�֪ͨ
static const EEquSrvEventType       EEQU_SRVEVENT_TRADE_ORDERQRY = 0x62;//����ί�в�ѯ--
static const EEquSrvEventType       EEQU_SRVEVENT_TRADE_ORDER = 0x63;	//����ί�б仯--
static const EEquSrvEventType       EEQU_SRVEVENT_TRADE_MATCHQRY = 0x64;//���׳ɽ���ѯ--
static const EEquSrvEventType       EEQU_SRVEVENT_TRADE_MATCH = 0x65;   //���׳ɽ��仯--
static const EEquSrvEventType       EEQU_SRVEVENT_TRADE_POSITQRY = 0x66;//���׳ֲֲ�ѯ--
static const EEquSrvEventType       EEQU_SRVEVENT_TRADE_POSITION = 0x67;//���׳ֱֲ仯--
static const EEquSrvEventType       EEQU_SRVEVENT_TRADE_FUNDQRY = 0x68; //�����ʽ��ѯ
static const EEquSrvEventType       EEQU_SRVEVENT_TRADE_USERQRY = 0x6B; //�ʽ��˺Ų�ѯ
static const EEquSrvEventType       EEQU_SRVEVENT_TRADE_EXCSTATEQRY = 0x6C;//������״̬��ѯ--
static const EEquSrvEventType       EEQU_SRVEVENT_TRADE_EXCSTATE = 0x6D;	//������״̬�仯֪ͨ--
//����������
typedef U32							EEquErrorCodeType;
typedef STR200                      EEquErrorTextType;              //������Ϣ

typedef PTR							EEquSrvDataType;				//����ָ��
typedef U8                          EEquSrvChainType;
static const EEquSrvChainType		EEQU_SRVCHAIN_END = '0';		//û�к�������
static const EEquSrvChainType		EEQU_SRVCHAIN_NOTEND = '1';		//�к�������
																
typedef U16                         EEquFieldSizeType;				//�����峤��
typedef U16                         EEquFieldCountType;				//���������

typedef U32                         EEquStrategyIdType;				//���Ա��
typedef STR50                       EEquStrategyNameType;			//��������

typedef U8                          EEquStrategyStateType;			//����״̬
static const EEquStrategyStateType	EEQU_STATE_RUN = '0';			//����
static const EEquStrategyStateType	EEQU_STATE_SUSPEND = '1';		//����
static const EEquStrategyStateType	EEQU_STATE_STOP = '2';			//ֹͣ

typedef STR50                       EEquSeriesNameType;				//ָ������
typedef STR50                       EEquItemNameType;				//ָ��������
typedef U32						    EEquSeriesThickType;			//�߶ο��
typedef I32						    EEquSeriesCoordType;			//����
typedef I32						    EEquSeriesIconType;				//ͼ�� ��
static const EEquSeriesIconType		EEQU_ICON_RUN = 0;				//��������
static const EEquSeriesIconType		EEQU_ICON_SMILE = 1;			//Ц��
static const EEquSeriesIconType		EEQU_ICON_CRYING = 2;			//����
static const EEquSeriesIconType		EEQU_ICON_UP = 3;				//�ϼ�ͷ
static const EEquSeriesIconType		EEQU_ICON_DOWN = 4;				//�¼�ͷ
static const EEquSeriesIconType		EEQU_ICON_UP2 = 5;				//�ϼ�ͷ2
static const EEquSeriesIconType		EEQU_ICON_DOWN2 = 6;			//�¼�ͷ2
static const EEquSeriesIconType		EEQU_ICON_HORN = 7;				//����
static const EEquSeriesIconType		EEQU_ICON_LOCK = 8;				//����
static const EEquSeriesIconType		EEQU_ICON_UNLOCK = 9;			//����
static const EEquSeriesIconType		EEQU_ICON_MONEYADD = 10;		//����+
static const EEquSeriesIconType		EEQU_ICON_MONEYSUB = 11;		//����-
static const EEquSeriesIconType		EEQU_ICON_ADD = 12;				//�Ӻ�
static const EEquSeriesIconType		EEQU_ICON_SUB = 13;				//����
static const EEquSeriesIconType		EEQU_ICON_WARNING = 14;			//̾��
static const EEquSeriesIconType		EEQU_ICON_ERROR = 15;			//���

typedef U32                         EEquColorType;				  	//��ɫ							    
typedef U32						    EEquDataCountType;				//����
typedef U32						    EEquParamNumType;				//��������
typedef U8						    EEquSeriesGroupType;			//����
								    
typedef STR20					    EEquParamNameType;				//������
typedef F64						    EEquParamValueType;				//����ֵ
								    
typedef B8						    EEquSeriesAxisType;				//�Ƿ��������
static const EEquSeriesAxisType	    EEQU_IS_AXIS = '0';				//����
static const EEquSeriesAxisType	    EEQU_ISNOT_AXIS = '1';			//�Ƕ���
								    
typedef U8						    EEquIsMain;						//����ͼ
static const EEquIsMain			    EEQU_IS_MAIN = '0';				//��ͼ
static const EEquIsMain			    EEQU_ISNOT_MAIN = '1';			//��ͼ 

typedef U8                          EEquSeriesType;				  	//����
static const EEquSeriesType			EEQU_VERTLINE = 0;				//��ֱֱ��
static const EEquSeriesType			EEQU_INDICATOR = 1;				//ָ����
static const EEquSeriesType			EEQU_BAR = 2;					//����
static const EEquSeriesType			EEQU_STICKLINE = 3;				//���߶�
static const EEquSeriesType			EEQU_COLORK = 4;				//��ɫK��
static const EEquSeriesType			EEQU_PARTLINE = 5;				//�߶�
static const EEquSeriesType			EEQU_ICON = 6;					//ͼ��
static const EEquSeriesType			EEQU_DOT = 7;					//��
static const EEquSeriesType			EEQU_ANY = 8;					//λ�ø�ʽ
static const EEquSeriesType			EEQU_TEXT = 9;					//�ı�

typedef C8                          STR19[20];
typedef STR19						EEquSigTextType;				//�ַ���

typedef STR10						EEquExchangeNoType;				//���������
typedef STR50						EEquExchangeNameType;			//����������

typedef STR20						EEquCommodityNoType;			//Ʒ�ֱ�ţ�����������Ʒ�����ͣ�
typedef STR50						EEquCommodityNameType;			//Ʒ������

typedef C8							EEquCommodityTypeType;			//Ʒ������
static const EEquCommodityTypeType  EEQU_COMMODITYTYPE_NONE = 'N';		//��
static const EEquCommodityTypeType  EEQU_COMMODITYTYPE_SPOT = 'P';		//�ֻ�
static const EEquCommodityTypeType  EEQU_COMMODITYTYPE_DEFER = 'Y';		//����
static const EEquCommodityTypeType  EEQU_COMMODITYTYPE_FUTURES = 'F';	//�ڻ�
static const EEquCommodityTypeType  EEQU_COMMODITYTYPE_OPTION = 'O';	//��Ȩ
static const EEquCommodityTypeType  EEQU_COMMODITYTYPE_MONTH = 'S';		//��������
static const EEquCommodityTypeType  EEQU_COMMODITYTYPE_COMMODITY = 'M';	//��Ʒ������
static const EEquCommodityTypeType  EEQU_COMMODITYTYPE_BUL = 'U';		//���Ǵ�ֱ����
static const EEquCommodityTypeType  EEQU_COMMODITYTYPE_BER = 'E';		//������ֱ����
static const EEquCommodityTypeType  EEQU_COMMODITYTYPE_STD = 'D';		//��ʽ����
static const EEquCommodityTypeType  EEQU_COMMODITYTYPE_STG = 'G';		//���ʽ����
static const EEquCommodityTypeType  EEQU_COMMODITYTYPE_PRT = 'R';		//�������
static const EEquCommodityTypeType  EEQU_COMMODITYTYPE_BLT = 'L';		//����ˮƽ��Ȩ
static const EEquCommodityTypeType  EEQU_COMMODITYTYPE_BRT = 'Q';		//����ˮƽ��Ȩ
static const EEquCommodityTypeType  EEQU_COMMODITYTYPE_DIRECT = 'X';	//��� ֱ�ӻ��� USD�ǻ������� USDxxx
static const EEquCommodityTypeType  EEQU_COMMODITYTYPE_INDIRECT = 'I';	//��� ��ӻ��� xxxUSD
static const EEquCommodityTypeType  EEQU_COMMODITYTYPE_CROSS = 'C';		//��� ������� xxxxxx
static const EEquCommodityTypeType  EEQU_COMMODITYTYPE_INDEX = 'Z';		//ָ��
static const EEquCommodityTypeType  EEQU_COMMODITYTYPE_STOCK = 'T';		//��Ʊ
static const EEquCommodityTypeType  EEQU_COMMODITYTYPE_SPDMON = 's';	//���ǿ��� SPD|s|SR|801|805
static const EEquCommodityTypeType  EEQU_COMMODITYTYPE_SPDCOM = 'm';	//���ǿ�Ʒ�� SPD|m|A+M2-B|805
static const EEquCommodityTypeType  EEQU_COMMODITYTYPE_SPDDEFER = 'y';	//���� SPD|m|A+M2-B|805

typedef F64							EEquCommodityNumeType;			//��С�䶯�� ����
typedef U16							EEquCommodityDenoType;			//��С�䶯�� ��ĸ
typedef F64							EEquCommodityTickType;			//��С�䶯�� ����/��ĸ
typedef U8							EEquCommodityPrecType;			//��С�䶯�� ����
typedef F32							EEquPriceMultipleType;			//ִ�м۸�������(��Ȩ��Լ������ִ�м۳��Դ˱�������������ͬ���ļ۸�)
typedef F64							EEquCommodityDotType;			//��Ʒ����

typedef STR100						EEquContractNoType;				//������Լ���
typedef STR100						EEquContractCodeType;			//��Լ��ʾ����
typedef STR100						EEquContractNameType;			//��Լ����

typedef C8							EEquCoverModeType;				//ƽ�ַ�ʽ
static const EEquCoverModeType		EEQU_COVERMODE_NONE = 'N';		//�����ֿ�ƽ
static const EEquCoverModeType		EEQU_COVERMODE_UNFINISH = 'U';	//ƽ��δ�˽�
static const EEquCoverModeType		EEQU_COVERMODE_COVER = 'C';		//���֡�ƽ��
static const EEquCoverModeType		EEQU_COVERMODE_TODAY = 'T';		//���֡�ƽ�֡�ƽ��

typedef C8							EEquDirect;						//����
typedef C8							EEquOffset;						//��ƽ
																	//������������---------------------------------------------------------------
typedef U8							EEquFidMeanType;			  	//�����ֶκ���
static const EEquFidMeanType		EEQU_FID_PRECLOSINGPRICE = 0;	//�����̼�
static const EEquFidMeanType		EEQU_FID_PRESETTLEPRICE = 1;	//������
static const EEquFidMeanType		EEQU_FID_PREPOSITIONQTY = 2;	//��ֲ���
static const EEquFidMeanType		EEQU_FID_OPENINGPRICE = 3;		//���̼�
static const EEquFidMeanType		EEQU_FID_LASTPRICE = 4;			//���¼�
static const EEquFidMeanType		EEQU_FID_HIGHPRICE = 5;			//��߼�
static const EEquFidMeanType		EEQU_FID_LOWPRICE = 6;			//��ͼ�
static const EEquFidMeanType		EEQU_FID_HISHIGHPRICE = 7;		//��ʷ��߼�
static const EEquFidMeanType		EEQU_FID_HISLOWPRICE = 8;		//��ʷ��ͼ�
static const EEquFidMeanType		EEQU_FID_LIMITUPPRICE = 9;		//��ͣ��
static const EEquFidMeanType		EEQU_FID_LIMITDOWNPRICE = 10;	//��ͣ��
static const EEquFidMeanType		EEQU_FID_TOTALQTY = 11;			//�����ܳɽ���
static const EEquFidMeanType		EEQU_FID_POSITIONQTY = 12;		//�ֲ���
static const EEquFidMeanType		EEQU_FID_AVERAGEPRICE = 13;		//����
static const EEquFidMeanType		EEQU_FID_CLOSINGPRICE = 14;		//���̼�
static const EEquFidMeanType		EEQU_FID_SETTLEPRICE = 15;		//�����
static const EEquFidMeanType		EEQU_FID_LASTQTY = 16;			//���³ɽ���
static const EEquFidMeanType		EEQU_FID_BESTBIDPRICE = 17;		//�������
static const EEquFidMeanType		EEQU_FID_BESTBIDQTY = 18;		//��������
static const EEquFidMeanType		EEQU_FID_BESTASKPRICE = 19;		//��������
static const EEquFidMeanType		EEQU_FID_BESTASKQTY = 20;		//��������
static const EEquFidMeanType		EEQU_FID_IMPLIEDBIDPRICE = 21;	//�������
static const EEquFidMeanType		EEQU_FID_IMPLIEDBIDQTY = 22;	//��������
static const EEquFidMeanType		EEQU_FID_IMPLIEDASKPRICE = 23;	//��������
static const EEquFidMeanType		EEQU_FID_IMPLIEDASKQTY = 24;	//��������
static const EEquFidMeanType		EEQU_FID_TOTALBIDQTY = 25;		//ί������
static const EEquFidMeanType		EEQU_FID_TOTALASKQTY = 26;		//ί������
static const EEquFidMeanType		EEQU_FID_TOTALTURNOVER = 27;	//�ܳɽ���
static const EEquFidMeanType		EEQU_FID_CAPITALIZATION = 28;	//����ֵ
static const EEquFidMeanType		EEQU_FID_CIRCULATION = 29;		//��ͨ��ֵ
static const EEquFidMeanType		EEQU_FID_THEORETICALPRICE = 30;	//���ۼ�
static const EEquFidMeanType		EEQU_FID_RATIO = 31;			//������ �Ǽ۸���
static const EEquFidMeanType		EEQU_FID_DELTA = 32;			//Delta
static const EEquFidMeanType		EEQU_FID_GAMMA = 33;			//Gamma
static const EEquFidMeanType		EEQU_FID_VEGA = 34;				//Vega
static const EEquFidMeanType		EEQU_FID_THETA = 35;			//Theta
static const EEquFidMeanType		EEQU_FID_RHO = 36;				//Rho
static const EEquFidMeanType		EEQU_FID_INTRINSICVALUE = 37;	//��Ȩ���ڼ�ֵ
static const EEquFidMeanType		EEQU_FID_UNDERLYCONT = 38;		//�����Լ��Ӧ�ı�ĺ�Լ
static const EEquFidMeanType		EEQU_FID_SubBidPrice1 = 39;		//���1
static const EEquFidMeanType		EEQU_FID_SubBidPrice2 = 40;		//���2
static const EEquFidMeanType		EEQU_FID_SubBidPrice3 = 41;		//���3
static const EEquFidMeanType		EEQU_FID_SubBidPrice4 = 42;		//���4
static const EEquFidMeanType		EEQU_FID_SubAskPrice1 = 43;		//����1
static const EEquFidMeanType		EEQU_FID_SubAskPrice2 = 44;		//����2
static const EEquFidMeanType		EEQU_FID_SubAskPrice3 = 45;		//����3
static const EEquFidMeanType		EEQU_FID_SubAskPrice4 = 46;		//����4
static const EEquFidMeanType		EEQU_FID_SubLastPrice1 = 47;	//���¼�1
static const EEquFidMeanType		EEQU_FID_SubLastPrice2 = 48;	//���¼�2
static const EEquFidMeanType		EEQU_FID_SubLastPrice3 = 49;	//���¼�3
static const EEquFidMeanType		EEQU_FID_SubLastPrice4 = 50;	//���¼�4
static const EEquFidMeanType		EEQU_FID_PreAveragePrice = 51;	//���վ���

static const EEquFidMeanType		EEQU_FID_TIMEVALUE = 111;		//��Ȩʱ���ֵ
static const EEquFidMeanType		EEQU_FID_UPDOWN = 112;			//�ǵ�
static const EEquFidMeanType		EEQU_FID_GROWTH = 113;			//�Ƿ�
static const EEquFidMeanType		EEQU_FID_NOWINTERST = 114;		//����
static const EEquFidMeanType		EEQU_FID_TURNRATE = 115;		//������
static const EEquFidMeanType		EEQU_FID_CODE = 122;			//��Լ����
static const EEquFidMeanType		EEQU_FID_SRCCODE = 123;			//ԭʼ��Լ����
static const EEquFidMeanType		EEQU_FID_NAME = 124;			//��Լ����
static const EEquFidMeanType		EEQU_FID_DATETIME = 125;		//����ʱ��												   
static const EEquFidMeanType		EEQU_FID_SPREADRATIO = 126;		//��������ϵ��

static const EEquFidMeanType		EEQU_FID_MEAN_COUNT = 128;		//�ֶ�������

typedef C8							EEquFidAttrType;			  	//�����ֶ�����
static const EEquFidAttrType		EEQU_FIDATTR_NONE = 0;			//��ֵ
static const EEquFidAttrType		EEQU_FIDATTR_VALID = 1;			//��ֵ
static const EEquFidAttrType		EEQU_FIDATTR_IMPLIED = 2;		//����

typedef C8							EEquFidTypeType;			  	//�ֶ���������
static const EEquFidTypeType		EEQU_FIDTYPE_NONE = 0;			//��Ч
static const EEquFidTypeType		EEQU_FIDTYPE_PRICE = 1;			//�۸�
static const EEquFidTypeType		EEQU_FIDTYPE_QTY = 2;			//����
static const EEquFidTypeType		EEQU_FIDTYPE_GREEK = 3;			//ϣ����ĸ
static const EEquFidTypeType		EEQU_FIDTYPE_DATETIME = 4;		//����ʱ��
static const EEquFidTypeType		EEQU_FIDTYPE_DATE = 5;			//����
static const EEquFidTypeType		EEQU_FIDTYPE_TIME = 6;			//ʱ��
static const EEquFidTypeType		EEQU_FIDTYPE_STATE = 7;			//״̬
static const EEquFidTypeType		EEQU_FIDTYPE_STR = 8;			//�ַ��� ���7�ֽ�
static const EEquFidTypeType		EEQU_FIDTYPE_PTR = 9;			//ָ��

static const EEquFidTypeType		EEQU_FIDTYPE_ARRAY[] =
{
	EEQU_FIDTYPE_PRICE, EEQU_FIDTYPE_PRICE, EEQU_FIDTYPE_QTY  , EEQU_FIDTYPE_PRICE, EEQU_FIDTYPE_PRICE, EEQU_FIDTYPE_PRICE, EEQU_FIDTYPE_PRICE, EEQU_FIDTYPE_PRICE, //0
	EEQU_FIDTYPE_PRICE, EEQU_FIDTYPE_PRICE, EEQU_FIDTYPE_PRICE, EEQU_FIDTYPE_QTY  , EEQU_FIDTYPE_QTY  , EEQU_FIDTYPE_PRICE, EEQU_FIDTYPE_PRICE, EEQU_FIDTYPE_PRICE, //8
	EEQU_FIDTYPE_QTY  , EEQU_FIDTYPE_PRICE, EEQU_FIDTYPE_QTY  , EEQU_FIDTYPE_PRICE, EEQU_FIDTYPE_QTY  , EEQU_FIDTYPE_PRICE, EEQU_FIDTYPE_QTY  , EEQU_FIDTYPE_PRICE, //16
	EEQU_FIDTYPE_QTY  , EEQU_FIDTYPE_QTY  , EEQU_FIDTYPE_QTY  , EEQU_FIDTYPE_PRICE, EEQU_FIDTYPE_PRICE, EEQU_FIDTYPE_PRICE, EEQU_FIDTYPE_PRICE, EEQU_FIDTYPE_GREEK, //24
	EEQU_FIDTYPE_GREEK, EEQU_FIDTYPE_GREEK, EEQU_FIDTYPE_GREEK, EEQU_FIDTYPE_GREEK, EEQU_FIDTYPE_GREEK, EEQU_FIDTYPE_PRICE , EEQU_FIDTYPE_STR , EEQU_FIDTYPE_PRICE, //32
	EEQU_FIDTYPE_PRICE, EEQU_FIDTYPE_PRICE, EEQU_FIDTYPE_PRICE, EEQU_FIDTYPE_PRICE, EEQU_FIDTYPE_PRICE, EEQU_FIDTYPE_PRICE, EEQU_FIDTYPE_PRICE, EEQU_FIDTYPE_PRICE, //40
	EEQU_FIDTYPE_PRICE, EEQU_FIDTYPE_PRICE, EEQU_FIDTYPE_PRICE, EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , //48
	EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , //56
	EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , //64
	EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , //72
	EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , //80
	EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , //88
	EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , //96
	EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_PRICE, //104
	EEQU_FIDTYPE_PRICE, EEQU_FIDTYPE_PRICE, EEQU_FIDTYPE_QTY  , EEQU_FIDTYPE_PRICE, EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , //112
	EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_NONE , EEQU_FIDTYPE_STR  , EEQU_FIDTYPE_STR  , EEQU_FIDTYPE_STR  , EEQU_FIDTYPE_DATETIME, EEQU_FIDTYPE_STR, EEQU_FIDTYPE_NONE, //120
};

static const U8						EEQU_MAX_L2_DEPTH = 10;				//L2������
typedef F64                         EEquPriceType;						//�۸�����
typedef U64                         EEquQtyType;						//��������
typedef C8                          EEquStateType;						//״̬����
typedef C8                          EEquStrType[8];						//�����ֶζ��ַ�������
typedef PTR                         EEquPtrType;						//ָ������
typedef F64                         EEquGreekType;						//ϣ����ĸ����
typedef F64                         EEquVolatilityType;					//����������
typedef STR20						EEquPriceStrType;					//�۸��ʽ��Ϊ��ʾ���ַ���
typedef U16                         EEquWidthType;						//�������
typedef U64                         EEquDateTimeType;			  		//����ʱ��
typedef U32                         EEquDateType;				  		//����
typedef U32                         EEquTimeType;				  		//ʱ��
typedef U16							EEquDaysType;				  		//������

typedef U8							EEquKLineSliceType;					//k��Ƭ������ ���룬����ӣ�����
typedef I32							EEquKLineIndexType;					//k������
typedef U32							EEquKLineCountType;					//k������

typedef C8							EEquKLineTypeType;				 	//k������
static const EEquKLineTypeType		EEQU_KLINE_TICK = 'T';				//�ֱ� RawKLineSliceType Ϊ0
static const EEquKLineTypeType		EEQU_KLINE_MINUTE = 'M';			//������
static const EEquKLineTypeType		EEQU_KLINE_DAY = 'D';				//����

typedef U8							EEquNeedNotice;
static const EEquNeedNotice			EEQU_NOTICE_NOTNEED = '0';			//��Ҫ����ˢ������
static const EEquNeedNotice			EEQU_NOTICE_NEED = '1';				//����Ҫ��������

typedef U32							EEquSessionIdType;					//���ĻỰ���
typedef U32							EEquLastQtyType;					//��ϸ���ֱ仯
typedef I32							EEquPositionChgType;				//��ϸ�ֱֲ仯

typedef I16							EEquTimeBucketIndexType;			//����ʱ��ģ��˳��
typedef I16							EEquTimeBucketCalCountType;			//����ʱ�μ��������

typedef C8										EEquTimeBucketTradeStateType;			//����ʱ��״̬ ����ʱ�ν���'3','4','5'�����齻��״̬������
static const EEquTimeBucketTradeStateType		EEQU_TRADESTATE_BID = '1';	//���Ͼ���
static const EEquTimeBucketTradeStateType		EEQU_TRADESTATE_MATCH = '2';	//���Ͼ��۴��
static const EEquTimeBucketTradeStateType		EEQU_TRADESTATE_CONTINUOUS = '3';	//��������
static const EEquTimeBucketTradeStateType		EEQU_TRADESTATE_PAUSED = '4';	//��ͣ
static const EEquTimeBucketTradeStateType		EEQU_TRADESTATE_CLOSE = '5';	//��ʽ
static const EEquTimeBucketTradeStateType		EEQU_TRADESTATE_DEALLAST = '6';	//���д���ʱ��
static const EEquTimeBucketTradeStateType		EEQU_TRADESTATE_SWITCHTRADE = '0';	//�������л�ʱ��
static const EEquTimeBucketTradeStateType		EEQU_TRADESTATE_UNKNOWN = 'N';	//δ֪״̬
static const EEquTimeBucketTradeStateType		EEQU_TRADESTATE_INITIALIZE = 'I';	//����ʼ��
static const EEquTimeBucketTradeStateType		EEQU_TRADESTATE_READY = 'R';	//׼������

typedef C8										EEquTimeBucketDateFlagType; 			//����ʱ�����ڱ�־ T-1,T,T+1
static const EEquTimeBucketDateFlagType			EEQU_DATEFLAG_PREDAY = '0';	//T-1
static const EEquTimeBucketDateFlagType			EEQU_DATEFLAG_CURDAY = '1';	//T
static const EEquTimeBucketDateFlagType			EEQU_DATEFLAG_NEXTDAY = '2';	//T+1

//��������Ϣ��ѯ����
typedef struct EEquExchangeReq
{
	EEquExchangeNoType              ExchangeNo;		//����������
} EEquExchangeReq;

//��������Ϣ��ѯ����
typedef struct EEquExchangeData
{
	EEquExchangeNoType              ExchangeNo;		//����������
	EEquExchangeNameType            ExchangeName;	//����������
} EEquExchangeData;

//Ʒ����Ϣ��ѯ������Ϣ
typedef struct EEquCommodityReq
{
	EEquCommodityNoType             CommodityNo;	//��մ�ͷ��ʼ�飬����ÿ�ΰ�Ӧ�����������
} EEquCommodityReq;

//Ʒ����Ϣ��ѯ����
typedef struct EEquCommodityData
{
	EEquExchangeNoType				ExchangeNo;	
	EEquCommodityNoType				CommodityNo;	//Ʒ�ִ���
	EEquCommodityTypeType			CommodityType;	//Ʒ������
	EEquCommodityNameType			CommodityName;	//Ʒ������
	EEquCommodityNumeType			PriceNume;		//����
	EEquCommodityDenoType			PriceDeno;		//��ĸ
	EEquCommodityTickType			PriceTick;		//��С�䶯��
	EEquCommodityPrecType			PricePrec;		//�۸񾫶�
	EEquCommodityDotType			TradeDot;		//ÿ�ֳ���
	EEquCoverModeType				CoverMode;		//ƽ�ַ�ʽ
} EEquCommodityData;

//��Լ��Ϣ��ѯ����
typedef struct EEquContractReq
{
	EEquContractNoType              ContractNo;		//��Լ���
} EEquContractReq;

//��Լ��Ϣ��ѯ����
typedef struct EEquContractData
{
	EEquExchangeNoType				ExchangeNo;		//������
	EEquCommodityNoType				CommodityNo;	//Ʒ�ִ���
	EEquContractNoType              ContractNo;     //��Լ���
} EEquContractData;

//���ĺ��˶�����, ��ͨ�����level2�����ʹ�ô˽ṹ
typedef struct EEquSnapShotReq
{
	EEquContractNoType				ContractNo;    //��Լ���(�ͻ������̨����ʹ�ú�Լ)

} EEquSnapShotReq;

//��������и��ֶ�
typedef struct EEquQuoteField
{
	union
	{
		EEquFidMeanType				FidMean;		//�仯����ʹ�ñ�ʶ
		EEquFidAttrType				FidAttr;		//�̶�����ʹ������
	};
	union
	{
		EEquPriceType				Price;
		EEquQtyType					Qty;
		EEquGreekType				Greek;
		EEquVolatilityType			Volatility;
		EEquDateTimeType			DateTime;
		EEquDateType				Date;
		EEquTimeType				Time;
		EEquStateType				State;
		EEquStrType					Str;
		EEquPtrType					Ptr;
	};
} EEquQuoteField;

//������ղ���					   
typedef struct EEquSnapShotData
{
	EEquDateTimeType				UpdateTime;     //�������ʱ��
	EEquFidMeanType					FieldCount;     //EquSnapShotField������
	EEquQuoteField	                FieldData[1];   //�����ֶε���ʼλ�ã�������ʱ�˽ṹ���������ֶγ���
} EEquSnapShotData;

//�������L2
typedef struct EEquQuoteFieldL2
{
	EEquPriceType					Price;
	EEquQtyType						Qty;
} EEquQuoteFieldL2;

typedef struct EEquQuoteSnapShotL2
{
	EEquQuoteFieldL2				BData[EEQU_MAX_L2_DEPTH];
	EEquQuoteFieldL2				SData[EEQU_MAX_L2_DEPTH];
} EEquQuoteSnapShotL2;

//K�߲�ѯ����
typedef struct EEquKLineReq
{
	EEquKLineCountType				ReqCount;        //������������չʹ�ã�
	EEquContractNoType              ContractNo;      //��ԼID
	EEquKLineTypeType               KLineType;       //K������
	EEquKLineSliceType              KLineSlice;      //K�߶���(0 tick) ���� ����
	EEquNeedNotice					NeedNotice;		//��Ҫ����֪ͨ
} EEquKLineReq;

typedef struct EEquKLineData //sizeof 80�ֽ�
{
	EEquKLineIndexType              KLineIndex;      //K������  tickÿ��������ţ�min���׷�����ţ�day��Ч
	EEquDateType					TradeDate;       //������   tick��Ч��min���ܺ�ʱ�����ͬ��day��ʱ�����ͬ
	EEquDateTimeType				DateTimeStamp;   //ʱ�������ͬ�������ͣ����Ȳ�ͬ
	EEquQtyType						TotalQty;       //������� �ܳɽ���
	EEquQtyType						PositionQty;    //������� �ֲ���
	EEquPriceType					LastPrice;      //���¼ۣ����̼ۣ�

	union
	{
		struct
		{
			EEquQtyType				KLineQty;       //K�߳ɽ��� day  min
			EEquPriceType			OpeningPrice;   //���̼�  day  min
			EEquPriceType			HighPrice;      //��߼�  day  min
			EEquPriceType			LowPrice;       //��ͼ�  day  min
			EEquPriceType			SettlePrice;    //�����  day  min

		};
		struct
		{
			EEquLastQtyType			LastQty;        //��ϸ����  tick
			EEquPositionChgType		PositionChg;    //�ֲ����仯 tick
			EEquPriceType			BuyPrice;       //��� tick
			EEquPriceType			SellPrice;      //���� tick
			EEquQtyType				BuyQty;         //���� tick
			EEquQtyType				SellQty;        //���� tick
		};
	};
} EEquKLineData;
	

//K�߲����л�
typedef struct EEquKLineStrategySwitch
{
	EEquStrategyIdType				StrategyId;		 //����ID
	EEquStrategyNameType			StrategyName;	 //��������
	EEquContractNoType              ContractNo;      //��ԼID
	EEquKLineTypeType               KLineType;       //K������
	EEquKLineSliceType				KLineSlice;		 //���� ���� ����
} EEquKLineStrategySwitch;

//K�߽������
typedef struct EEquKLineDataResult
{
	EEquStrategyIdType				StrategyId;		 //���Ա��

	EEquKLineCountType				Count;			 //����
	EEquKLineData					*Data;		     //����
} EEquKLineDataResult;

typedef struct EEquKLineSeries
{
	EEquKLineIndexType				KLineIndex;		//����0��Ч
	EEquPriceType					Value;			//InvalidNumeric ��ʾ��Ч����
	union
	{
		struct //��ɫK��,��ֱ��
		{
			EEquColorType			ClrK;
		};

		struct //ͼ������,������
		{
			EEquSeriesIconType		Icon;
		};

		struct //����
		{
			EEquColorType			ClrStick;
			EEquPriceType			StickValue;
		};

		struct  //����
		{
			EEquColorType			ClrBar;
			B8						Filled;
			EEquPriceType			BarValue;
		};

		struct  //�߶�		  `
		{
			EEquSeriesCoordType		Idx2;	        //�߶ε�ĩ��K������
			EEquColorType			ClrLine;	    //�߶���ɫ
			EEquPriceType			LineValue;		//�߶�ĩ������
			EEquSeriesThickType		LinWid;			//�߶ο��
		};
		struct //�ı�
		{
			EEquSigTextType			Text;		
		};
	};
}EEquKLineSeries;

//������Ϣ
typedef struct EEquSeriesParam
{
	EEquParamNameType				ParamName;		//������
	EEquParamValueType				ParamValue;		//����ֵ
}EEquSeriesParam;

//K��ָ�����
typedef struct EEquKLineSeriesInfo
{
	EEquItemNameType				ItemName;		//����ָ���� ����
	EEquSeriesType					Type;			//����	
	EEquColorType					Color;			//��ɫ
	EEquSeriesThickType				Thick;			//�߿�
	EEquSeriesAxisType				OwnAxis;		//�Ƿ��������
	
	EEquSeriesParam					Param[10];		//���� Max10
	EEquParamNumType				ParamNum;		//��������
	EEquSeriesGroupType				Groupid;		//��� 
	EEquSeriesNameType				GroupName;		//������ָ������
	EEquIsMain						Main;			//0-��ͼ 1-��ͼ1
	
	EEquStrategyIdType				StrategyId;		//����ID
} EEquKLineSeriesInfo;

//K��ָ������
typedef struct EEquKLineSeriesResult
{
	EEquStrategyIdType				StrategyId;		 //���Ա��
	EEquSeriesNameType				SeriesName;		 //ָ������

	EEquSeriesType					SeriesType;		 //ָ������		//����
	EEquIsMain						IsMain;			 //��ͼ ��ͼ	//����

	EEquKLineCountType				Count;			 //����
	EEquKLineSeries					*Data;		     //����
} EEquKLineSeriesResult;

typedef EEquKLineSeriesInfo			EEquKLineSignalInfo;

//�ź�����
typedef struct EEquSignalItem
{
	EEquKLineIndexType				KLineIndex;		//K������
	EEquContractNoType              ContractNo;     //��ԼID
	EEquDirect						Direct;			//��������
	EEquOffset						Offset;			//��ƽ
	EEquPriceType					Price;			//�۸�
	EEquQtyType						Qty;			//����
		
}EEquSignalItem;

//K���ź�����
typedef struct EEquKLineSignalResult
{
	EEquStrategyIdType				StrategyId;		//����ID
	EEquSeriesNameType				SeriesName;		//�ź�����
	
	EEquDataCountType				Count;			//����
	EEquSignalItem					*Data;			//����
} EEquKLineSignalResult;

//K��biao����
typedef struct EEquStrategyDataUpdateNotice
{
	EEquStrategyIdType				StrategyId;		//����ID
} EEquStrategyDataUpdateNotice;

//����״̬����
typedef struct EEquKlineStrategyStateNotice
{
	EEquStrategyIdType				StrategyId;		//����ID
	EEquStrategyStateType			StrategyState;	//����״̬
} EEquKlineStrategyStateNotice;

typedef EEquCommodityReq			EEquCommodityTimeBucketReq;
//ʱ��ģ��
typedef struct EEquHisQuoteTimeBucket
{
	EEquTimeBucketIndexType			Index;
	EEquTimeType					BeginTime;
	EEquTimeType					EndTime;
	EEquTimeBucketTradeStateType	TradeState;
	EEquTimeBucketDateFlagType		DateFlag;
	EEquTimeBucketCalCountType		CalCount;						//����ģ���Ӧ����ģ��ķ�����
	EEquCommodityNoType				Commodity;
} EEquHisQuoteTimeBucket;
///////////////////////////////////////////////////////////����///////////////////////////////////////////////////////////

typedef STR20 						EEquLoginNoType;					//��¼�˺�
typedef STR20 						EEquLoginNameType;					//��¼����
typedef C8							EEquUserType;						//�û�����
typedef STR20 						EEquUserNoType;						//�ʽ��˺�
typedef STR20 						EEquUserNameType;					//�ʽ��˻�����
typedef STR20 						EEquSignType;						//��������ʶ
typedef U32							EEquCountType;						//��������
typedef STR50						EEquLoginApiType;					//API����
typedef STR10						EEquTradeDateType;					//������
typedef C8							EEquReadyType;						//��ʼ����� 0δ��� 1���
static const EEquReadyType			EEQU_READY			= '1';			//���
static const EEquReadyType			EEQU_NOTREADY		= '0';			//δ���
typedef C8							EEquNextType;						//�Ƿ���Ų�ѯ

typedef STR20						EEquCurrencyNoType;					//����
typedef F64                         EEquExchangeRateType;				//���ֻ���
typedef F64                         EEquMoneyValueType;					//�ʽ���Ϣ
typedef STR20                       EEquUpdateTimeType;					//����ʱ��
typedef STR20                       EEquValidTimeType;					//��Чʱ��
typedef STR50                       EEquRemarkInfoType;					//��ע
typedef U32							EEquOrderIdType;					//������
typedef STR20	                    EEquOrderNoType;					//ί�к�
typedef STR20	                    EEquMatchNoType;					//�ɽ���
typedef STR50	                    EEquPositionNoType;					//�ֲֺ�
typedef STR50						EEquSystemNo;						//ϵͳ��
typedef I32							EEquErrorCode;						//������
typedef STR200						EEquErrorText;						//������Ϣ

typedef C8	 EEquOrderType;			//��������
static const EEquOrderType			otUnDefine = 'U';//δ����
static const EEquOrderType			otMarket = '1';//�м۵�
static const EEquOrderType			otLimit = '2';//�޼۵�
static const EEquOrderType			otMarketStop = '3';//�м�ֹ��
static const EEquOrderType			otLimitStop = '4';//�޼�ֹ��
static const EEquOrderType			otExecute = '5';//��Ȩ
static const EEquOrderType			otAbandon = '6';//��Ȩ
static const EEquOrderType			otEnquiry = '7';//ѯ��
static const EEquOrderType			otOffer = '8';//Ӧ��
static const EEquOrderType			otIceberg = '9';//��ɽ��
static const EEquOrderType			otGhost = 'A';//Ӱ�ӵ�
static const EEquOrderType			otSwap = 'B';//����
static const EEquOrderType			otSpreadApply = 'C';//��������
static const EEquOrderType			otHedgApply = 'D';//�ױ�����
static const EEquOrderType			otOptionAutoClose = 'F';//��Ȩǰ��Ȩ�ԶԳ�����
static const EEquOrderType			otFutureAutoClose = 'G';//��Լ�ڻ��ԶԳ�����
static const EEquOrderType			otMarketOptionKeep = 'H';//����������

typedef C8	 EEquValidType;			//��Ч����
static const EEquValidType			vtNone = 'N';//��
static const EEquValidType			vtFOK = '4';//��ʱȫ��
static const EEquValidType			vtIOC = '3';//��ʱ����
static const EEquValidType			vtGFD = '0';//������Ч
static const EEquValidType			vtGTC = '1';//������Ч
static const EEquValidType			vtGTD = '2';//������Ч

typedef C8	 EEquDirect;				//����
static const EEquDirect				dNone = 'N';
static const EEquDirect				dBuy = 'B';//����
static const EEquDirect				dSell = 'S';//����
static const EEquDirect				dBoth = 'A';//˫��

typedef C8	 EEquOffset;				//��ƽ
static const EEquOffset				oNone = 'N';//��
static const EEquOffset				oOpen = 'O';//����
static const EEquOffset				oCover = 'C';//ƽ��
static const EEquOffset				oCoverT = 'T';//ƽ��
static const EEquOffset				oOpenCover = '1';//��ƽ��Ӧ��ʱ��Ч, ��������Ҳ����
static const EEquOffset				oCoverOpen = '2';//ƽ����Ӧ��ʱ��Ч, ��������Ҳ����

typedef C8   EEquHedge;				//Ͷ�����
static const EEquHedge				hNone = 'N';//��
static const EEquHedge				hSpeculate = 'T';//Ͷ��
static const EEquHedge				hHedge = 'B';//�ױ�
static const EEquHedge				hSpread = 'S';//����
static const EEquHedge				hMarket = 'M';//����

typedef C8   EEquOrderState;		 //����״̬
static const EEquOrderState			osNone = 'N';//��
static const EEquOrderState			osSended = '0';//�ѷ���
static const EEquOrderState			osAccept = '1';//������
static const EEquOrderState			osTriggering = '2';//������
static const EEquOrderState			osActive = '3';//����Ч
static const EEquOrderState			osQueued = '4';//���Ŷ�
static const EEquOrderState			osPartFilled = '5';//���ֳɽ�
static const EEquOrderState			osFilled = '6';//��ȫ�ɽ�
static const EEquOrderState			osCanceling = '7';//����
static const EEquOrderState			osModifying = '8';//����
static const EEquOrderState			osCanceled = '9';//�ѳ���
static const EEquOrderState			osPartCanceled = 'A';//�ѳ��൥
static const EEquOrderState			osFail = 'B';//ָ��ʧ��
static const EEquOrderState			osChecking = 'C';//�����
static const EEquOrderState			osSuspended = 'D';//�ѹ���
static const EEquOrderState			osApply = 'E';//������
static const EEquOrderState			osInvalid = 'F';//��Ч��
static const EEquOrderState			osPartTriggered = 'G';//���ִ���
static const EEquOrderState			osFillTriggered = 'H';//��ȫ����
static const EEquOrderState			osPartFailed = 'I';//�൥ʧ��


typedef C8	 EEquStrategyType;		//��������
static const EEquStrategyType		stNone = 'N'; //��
static const EEquStrategyType		stPreOrder = 'P'; //Ԥ����(��)
static const EEquStrategyType		stAutoOrder = 'A'; //�Զ���
static const EEquStrategyType		stCondition = 'C'; //������

typedef C8	 EEquUserType;			//�û����
static const EEquUserType			uiNone = 'n';
static const EEquUserType			uiUnDefine = 'u';//δ����
static const EEquUserType			uiUser = 'c';//���ͻ�
static const EEquUserType			uiProxy = 'd';//�µ���
static const EEquUserType			uiBroker = 'b';//������
static const EEquUserType			uiTrader = 't';//����Ա
static const EEquUserType			uiQUser = 'q';//����ͻ�

typedef C8	 EEquCoverMode;			//ƽ�ַ�ʽ
static const EEquCoverMode			cmNone = 'N';//�����ֿ�ƽ
static const EEquCoverMode			cmUnfinish = 'U';//ƽ��δ�˽�
static const EEquCoverMode			cmCover = 'C';//���֡�ƽ��
static const EEquCoverMode			cmCoverToday = 'T';//���֡�ƽ�֡�ƽ��

typedef C8   EEquTrigMode;			 //����ģʽ
static const EEquTrigMode			tmNone = 'N';//��
static const EEquTrigMode			tmLatest = 'L';//���¼�
static const EEquTrigMode			tmBid = 'B';//���
static const EEquTrigMode			tmAsk = 'A';//����

typedef C8	 EEquTrigCond;			//��������
static const EEquTrigCond			tcNone = 'N';//��
static const EEquTrigCond			tcGreater = 'g';//����
static const EEquTrigCond			tcGreaterEEqual = 'G';//���ڵ���
static const EEquTrigCond			tcLess = 'l';//С��
static const EEquTrigCond			tcLessEEqual = 'L';//С�ڵ���

typedef C8   EEquTradeSect;			//����ʱ��
static const EEquTradeSect			tsDay = 'D'; //���콻��ʱ��
static const EEquTradeSect			tsNight = 'N'; //���ϣ�T+1������ʱ��
static const EEquTradeSect			tsAll = 'A'; //ȫ����ʱ��

typedef C8   EEquBoolType;			//�Ƿ�
static const EEquBoolType			bYes = 'Y'; //��
static const EEquBoolType			bNo = 'N'; //��

typedef STR20						EEquExchDateTimeType;				//������ʱ��

typedef C8	 EEquTradeState;
static const EEquTradeState			tsUnknown = 'N'; //δ֪״̬
static const EEquTradeState			tsIniting = 'I'; //����ʼ��
static const EEquTradeState			tsReady = 'R'; //׼������
static const EEquTradeState			tsSwitchDay = '0'; //�������л�
static const EEquTradeState			tsBiding = '1'; //�����걨
static const EEquTradeState			tsMakeMatch = '2'; //���۴��
static const EEquTradeState			tsTradeing = '3'; //��������
static const EEquTradeState			tsPause = '4'; //������ͣ
static const EEquTradeState			tsClosed = '5'; //���ױ���   
static const EEquTradeState			tsBidPause = '6'; //������ͣ
static const EEquTradeState			tsGatewayDisconnect = '7'; //����δ��
static const EEquTradeState			tsTradeDisconnect = '8'; //����δ��
static const EEquTradeState			tsCloseDeal = '9'; //���д���

//��½�˺Ų�ѯ����
typedef struct EEquLoginInfoReq
{
	EEquLoginNoType					LoginNo;
	EEquSignType					Sign;
}EEquLoginInfoReq;
//��¼�˺Ų�ѯӦ��
typedef struct EEquLoginInfoRsp
{
	EEquLoginNoType					LoginNo;
	EEquSignType					Sign;
	EEquLoginNameType				LoginName;
	EEquLoginApiType				LoginApi;
	EEquTradeDateType				TradeDate;
	EEquReadyType					IsReady;
}EEquLoginInfoRsp;

//�ʽ��˺Ų�ѯ����
typedef struct EEquUserInfoReq
{
	EEquLoginNoType					UserNo;
	EEquSignType					Sign;
}EEquUserInfoReq;
//�ʽ��˺Ų�ѯӦ��
typedef struct EEquUserInfoRsp
{
	EEquUserNoType					UserNo;
	EEquSignType					Sign;
	EEquLoginNoType					LoginNo;
	EEquUserNameType				UserName;
}EEquUserInfoRsp;

//�ʽ��ѯ����
typedef struct EEquUserMoneyReq
{
	EEquUserNoType					UserNo;					//��Ϊ��
	EEquSignType					Sign;					//��Ϊ��
	EEquCurrencyNoType				CurrencyNo;				//�� ȫ��
}EEquUserMoneyReq;

//�ʽ��ѯӦ��
typedef struct EEquUserMoneyRsp
{
	EEquUserNoType					UserNo;
	EEquSignType					Sign;
	EEquCurrencyNoType				CurrencyNo;				//���ֺ�(Currency_Base��ʾ����������ʽ�)
	EEquExchangeRateType			ExchangeRate;			//���ֻ���

	EEquMoneyValueType				FrozenFee;				//����������20
	EEquMoneyValueType				FrozenDeposit;			//���ᱣ֤��19
	EEquMoneyValueType				Fee;					//������(��������������)
	EEquMoneyValueType				Deposit;				//��֤��

	EEquMoneyValueType				FloatProfit;			//����LME�ֲ�ӯ��,���� market to market
	EEquMoneyValueType				FloatProfitTBT;			//��ʸ�Ӯ trade by trade
	EEquMoneyValueType				CoverProfit;			//ƽӯ ����
	EEquMoneyValueType				CoverProfitTBT;			//���ƽӯ

	EEquMoneyValueType				Balance;				//���ʽ�=PreBalance+Adjust+CashIn-CashOut-Fee(TradeFee+DeliveryFee+ExchangeFee)+CoverProfitTBT+Premium 
	EEquMoneyValueType				Equity;					//��Ȩ��=Balance+FloatProfitTBT(NewFloatProfit+LmeFloatProfit)+UnExpiredProfit
	EEquMoneyValueType				Available;				//�����=Equity-Deposit-Frozen(FrozenDeposit+FrozenFee)

	EEquUpdateTimeType				UpdateTime;				//����ʱ��
}EEquUserMoneyRsp;

//ί�в�ѯ����
typedef struct EEquOrderQryReq
{
	EEquUserNoType					UserNo;
	EEquSignType					Sign;
}EEquOrderQryReq;

//ί������
typedef struct EEquOrderInsertReq
{
	EEquUserNoType					UserNo;
	EEquSignType					Sign;
	EEquContractNoType				Cont;					//�����Լ
	EEquOrderType					OrderType;				//�������� 
	EEquValidType					ValidType;				//��Ч���� 
	EEquValidTimeType				ValidTime;				//��Ч����ʱ��(GTD�����ʹ��)
	EEquDirect						Direct;					//�������� 
	EEquOffset						Offset;					//����ƽ�� �� Ӧ�����뿪ƽ 
	EEquHedge						Hedge;					//Ͷ����ֵ 
	EEquPriceType					OrderPrice;				//ί�м۸� �� ��ȨӦ������۸�
	EEquPriceType					TriggerPrice;			//�����۸�
	EEquTrigMode					TriggerMode;			//����ģʽ
	EEquTrigCond					TriggerCondition;		//��������
	EEquQtyType						OrderQty;				//ί������ �� ��ȨӦ������
	EEquStrategyType				StrategyType;			//��������
	EEquRemarkInfoType				Remark;					//�µ���ע�ֶΣ�ֻ���µ�ʱ��Ч�������ҪΨһ��ʶһ����һ�鶨���������GUID����ʶ��������ܺ������µ�;����ID�ظ�
	EEquTradeSect					AddOneIsValid;			//T+1ʱ����Ч(���۽���)
}EEquOrderInsertReq;
//ί�г���
typedef struct EEquOrderCancelReq
{
	EEquOrderIdType					OrderId;				//������
}EEquOrderCancelReq;
//ί�иĵ�
typedef struct EEquOrderModifyReq
{
	EEquUserNoType					UserNo;
	EEquSignType					Sign;
	EEquContractNoType				Cont;					//�����Լ
	EEquOrderType					OrderType;				//�������� 
	EEquValidType					ValidType;				//��Ч���� 
	EEquValidTimeType				ValidTime;				//��Ч����ʱ��(GTD�����ʹ��)
	EEquDirect						Direct;					//�������� 
	EEquOffset						Offset;					//����ƽ�� �� Ӧ�����뿪ƽ 
	EEquHedge						Hedge;					//Ͷ����ֵ 
	EEquPriceType					OrderPrice;				//ί�м۸� �� ��ȨӦ������۸�
	EEquPriceType					TriggerPrice;			//�����۸�
	EEquTrigMode					TriggerMode;			//����ģʽ
	EEquTrigCond					TriggerCondition;		//��������
	EEquQtyType						OrderQty;				//ί������ �� ��ȨӦ������
	EEquStrategyType				StrategyType;			//��������
	EEquRemarkInfoType				Remark;					//�µ���ע�ֶΣ�ֻ���µ�ʱ��Ч�������ҪΨһ��ʶһ����һ�鶨���������GUID����ʶ��������ܺ������µ�;����ID�ظ�
	EEquTradeSect					AddOneIsValid;			//T+1ʱ����Ч(���۽���)

	EEquOrderIdType					OrderId;				//������
}EEquOrderModifyReq;
//ί��֪ͨ
typedef struct EEquOrderDataNotice
{
	EEquSessionIdType				SessionId;				//�Ự��
	EEquUserNoType					UserNo;
	EEquSignType					Sign;
	EEquContractNoType				Cont;					//�����Լ
	EEquOrderType					OrderType;				//�������� 
	EEquValidType					ValidType;				//��Ч���� 
	EEquValidTimeType				ValidTime;				//��Ч����ʱ��(GTD�����ʹ��)
	EEquDirect						Direct;					//�������� 
	EEquOffset						Offset;					//����ƽ�� �� Ӧ�����뿪ƽ 
	EEquHedge						Hedge;					//Ͷ����ֵ 
	EEquPriceType					OrderPrice;				//ί�м۸� �� ��ȨӦ������۸�
	EEquPriceType					TriggerPrice;			//�����۸�
	EEquTrigMode					TriggerMode;			//����ģʽ
	EEquTrigCond					TriggerCondition;		//��������
	EEquQtyType						OrderQty;				//ί������ �� ��ȨӦ������
	EEquStrategyType				StrategyType;			//��������
	EEquRemarkInfoType				Remark;					//�µ���ע�ֶΣ�ֻ���µ�ʱ��Ч�������ҪΨһ��ʶһ����һ�鶨���������GUID����ʶ��������ܺ������µ�;����ID�ظ�
	EEquTradeSect					AddOneIsValid;			//T+1ʱ����Ч(���۽���)

	EEquOrderState					OrderState;				//ί��״̬
	EEquOrderIdType					OrderId;				//������
	EEquOrderNoType					OrderNo;				//ί�к�
	EEquPriceType					MatchPrice;				//�ɽ���
	EEquQtyType						MatchQty;				//�ɽ���
	EEquErrorCode					ErrorCode;				//������Ϣ��				
	EEquErrorText					ErrorText;				//���´�����Ϣ
	EEquUpdateTimeType				InsertTime;				//�µ�ʱ��
	EEquUpdateTimeType				UpdateTime;				//����ʱ��
}EEquOrderDataNotice;

typedef EEquOrderQryReq				EEquMatchQryReq;		//�ɽ���ѯ�ṹ
//�ɽ����ݲ�ѯӦ��/֪ͨ
typedef struct EEquMatchNotice
{
	EEquUserNoType					UserNo;
	EEquSignType					Sign;
	EEquContractNoType				Cont;					//�����Լ
	EEquDirect						Direct;					//�������� 
	EEquOffset						Offset;					//����ƽ�� �� Ӧ�����뿪ƽ 
	EEquHedge						Hedge;					//Ͷ����ֵ 
	EEquOrderNoType					OrderNo;				//ί�к�
	EEquPriceType					MatchPrice;				//�ɽ���
	EEquQtyType						MatchQty;				//�ɽ���
	EEquCurrencyNoType				FeeCurrency;			//�����ѱ���
	EEquMoneyValueType				MatchFee;				//�ɽ�������
	EEquUpdateTimeType				MatchDateTime;			//����ʱ��
	EEquBoolType					AddOne;					//T+1�ɽ�
	EEquBoolType					Deleted;				//�Ƿ�ɾ��
}EEquMatchNotice;

//�ֲֲ�ѯ����ṹ
typedef EEquOrderQryReq				EEquPositionQryReq;		
//�ֲ����ݲ�ѯӦ��֪ͨ
typedef struct EEquPositionNotice
{
	EEquPositionNoType				PositionNo;
	EEquUserNoType					UserNo;
	EEquSignType					Sign;
	EEquContractNoType				Cont;					//�����Լ
	EEquDirect						Direct;					//�������� 
	EEquHedge						Hedge;					//Ͷ����ֵ 
	EEquMoneyValueType				Deposit;				//�ͻ���ʼ��֤��
	EEquQtyType						PositionQty;			//�ֲܳ���	
	EEquQtyType					    PrePositionQty;			//�������
	EEquPriceType					PositionPrice;			//�۸�
	EEquPriceType					ProfitCalcPrice;		//��ӯ�����
	EEquMoneyValueType				FloatProfit;			//��ӯ
	EEquMoneyValueType				FloatProfitTBT;			//��ʸ�Ӯ trade by trade
}EEquPositionNotice;


//////////////////////////////////////////////////////////////////////////////////////////
//������Ϣ
typedef struct EEquServiceInfo
{
	EEquSrvSrcType					SrvSrc;
	EEquSrvEventType				SrvEvent;
	EEquSrvChainType                SrvChain;
	EEquRetType                     SrvErrorCode;
	EEquErrorTextType               SrvErrorText;
	EEquSrvDataType                 SrvData;
	EEquFieldSizeType               DataFieldSize;
	EEquFieldCountType				DataFieldCount;
	
	EEquUserNoType					UserNo;

	EEquContractNoType				ContractNo;
	EEquKLineTypeType				KLineType;
	EEquKLineSliceType				KLineSlice;
	EEquSessionIdType				SessionId;
} EEquServiceInfo;

//�г�״̬ ʱ���ѯ����
typedef struct EEquExchangeStateReq
{
}EEquExchangeStateReq;
//�г�״̬ ʱ���ѯӦ��
typedef struct EEquExchangeStateRsp
{
	EEquSignType					Sign;
	EEquExchangeNoType				ExchangeNo;
	EEquExchDateTimeType			ExchangeDateTime;
	EEquExchDateTimeType			LocalDateTime;
	EEquTradeState					TradeState;
}EEquExchangeStateRsp;

typedef EEquExchangeStateRsp		EEquExchangeStateNotice;

//����ӳ����Ϣ��ѯ����
typedef struct EEquSpreadMappingReq
{
} EEquContractMappingReq;

//����ӳ����Ϣ��ѯ����
typedef struct EEquSpreadMappingData
{
	EEquContractNoType              ContractNo;     //�ͻ��˺�Լ���
	EEquContractNoType              SrcContractNo;  //ԭʼ��Լ���
} EEquSpreadMappingData;

//����ӳ����Ϣ��ѯ����
typedef EEquSpreadMappingReq EEquUnderlayMappingReq;

//����ӳ����Ϣ��ѯ����
typedef struct EEquUnderlayMappingData
{
	EEquContractNoType              ContractNo;			//�����Լ���
	EEquContractNoType              UnderlayContractNo; //��ʵ��Լ���
} EEquUnderlayMappingData;

#pragma pack(pop)

#endif // !EQUANTAPI_TYPE_H

