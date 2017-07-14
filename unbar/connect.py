import cx_Oracle

def get_status(servicenum): 
  status = []
  status = check_brm(servicenum, status)
  status = check_mvne(servicenum, status)
  status = check_crm(servicenum, status)
  status = get_last_SO(servicenum, status)
  return status

def check_brm(servicenum, status):
  con = cx_Oracle.connect('dbmamis/dbmamis123@10.35.242.100:1521/megatron')
  cur = con.cursor()
  sql = """SELECT bi.bill_info_id,
  s.poid_id0 service_poid,
  s.poid_type service_type,
  sal1.name duo_no,
  SUBSTR(sal2.name, 2, 13) service_no,
  DECODE(s.status, 10100, 'Active', 10102, 'Suspended', 10103, 'Disconnected') status,
  DECODE(aac_access, 1, 'SL Barred', 2, 'CL Barred', 0, 'Active', NULL, 'Active') barring_status,
  ccp.credit_limit,
  NVL(
  (SELECT SUM(due) FROM pin.item_t@BRM_PROD WHERE billinfo_obj_id0 = bi.poid_id0
  ),0) account_total_due
FROM pin.billinfo_t@BRM_PROD bi,
  pin.service_t@BRM_PROD s,
  pin.service_alias_list_t@BRM_PROD sal1,
  pin.service_alias_list_t@BRM_PROD sal2,
  pin.bal_grp_bals_t@BRM_PROD bgb,
  pin.cfg_credit_profile_t@BRM_PROD ccp
WHERE bi.bal_grp_obj_id0 = s.bal_grp_obj_id0 
AND bi.bal_grp_obj_id0   = bgb.obj_id0 
AND bgb.credit_profile   = ccp.REC_ID 
AND s.poid_id0           = sal1.obj_id0 (+)
AND sal1.rec_id (+)      = 0
AND s.poid_id0           = sal2.obj_id0 (+)
AND sal2.rec_id (+)      = 1
AND bgb.rec_id           = 608
--AND bi.bill_info_id      = '800578744'
AND sal2.name LIKE '%{0}%'  """.format(str(servicenum))
  cur.execute(sql)
  result = cur.fetchone()
  status.append(servicenum) #service number
  status.append(result[0]) #billing profile
  status.append(result[6]) #barring status
  status.append(result[7]) #credit limit
  status.append(result[8]) #total dues
  cur.close()
  con.close()
  return status


def check_mvne(servicenum, status):
  con = cx_Oracle.connect('dbmamis/dbmamis123@10.35.242.100:1521/megatron')
  cur = con.cursor()
  sql = 'SELECT  MVNE_Status FROM TABLE(nelzki.getsubs_api({0}))'.format(str(servicenum))
  cur.execute(sql)
  result = cur.fetchone()
  status.append(result[0]) #mvne status
  cur.close()
  con.close()
  return status


def check_crm(servicenum, status):
  con = cx_Oracle.connect('dbmamis/dbmamis123@10.35.242.100:1521/megatron')
  cur = con.cursor()
  sql = '''select
           asset_num,status_cd as status,x_bar_status as barstatus
           from s_asset@CRM_PROD
           where serial_num ='{0}' '''.format(str(servicenum))
  cur.execute(sql)
  result = cur.fetchone()
  status.append(result[2]) #barring status
  status.append(result[1]) #asset status
  cur.close()
  con.close()
  return status

def get_last_SO(servicenum, status):
  con = cx_Oracle.connect('dbmamis/dbmamis123@10.35.242.100:1521/megatron')
  cur = con.cursor()
  sql = '''SELECT * FROM (
            SELECT distinct(so.order_num), so.status_cd as Header_Status,
            soi.status_cd as Line_Status,
            soi.service_num as Service_Num,
            so.carrier_cd as Order_Type,
            sox.attrib_03      AS ORDER_REASON,
            sox.attrib_13 as Completion_Date, 
            COALESCE(sox.attrib_26, SYSDATE) as Submisison_Date
            FROM S_ORDER_ITEM@CRM_PROD soi, s_order@CRM_PROD so, s_order_x@CRM_PROD sox
            WHERE
            soi.ORDER_ID = so.row_id
            and so.row_id = sox.par_row_id
            and so.status_cd <> 'Cancelled'
            and soi.service_num = '{0}'
            order by sox.attrib_13 desc
            )
            WHERE ROWNUM = 1'''.format(str(servicenum))
  cur.execute(sql)
  result = cur.fetchone()
  status.append(result[0]) #SO
  status.append(result[2]) #Status
  status.append(result[4]) #Order Type
  status.append(result[5]) #Order Reason
  cur.close()
  con.close()
  return status