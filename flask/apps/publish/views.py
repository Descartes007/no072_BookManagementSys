
'''
**************************************************************
** @Create：2024/2/26 10:50
** @Author：anonymous
** @Description：
**************************************************************
'''
import json
from flask import Blueprint, request, jsonify, session


from sqlalchemy import or_, func
from apps.book.model import *
from apps.publish.model import Publisher
from exts.auth import require_access_token
from exts.common import insert_audit_log
from exts.logHandler import base_logger as logger
from exts.logHandler import audit_logger

publisher_bp = Blueprint('publisher', __name__)
model_name='出版社管理'
@publisher_bp.route('/publishing/add', methods=['POST'])
@require_access_token
def publishing_add(current_user):
    # 查询条目是否存在
    publish = Publisher.query.filter_by(name=request.get_json()["name"]).first()
    if publish is None:
        max_id_query = db.session.query(func.max(Publisher.id)).scalar()
        if max_id_query is None:
            max_id = 0
        else:
            max_id = max_id_query
        try:
            col = Publisher(publish_id=max_id + 1, name=request.get_json()["name"])
            db.session.add(col)  # 添加一条
            # 提交事务
            db.session.commit()
            response = {"code": 0, "message": "创建成功!", "status": True}
            # audit_logger.debug("[{0}] [{1}] [{2}] [添加出版社:{3}]".format(request.remote_addr, current_user ,model_name,request.get_json()['name']))
            insert_audit_log(request.remote_addr, current_user, model_name, '添加出版社: ' + request.get_json()["name"])
        except Exception as e:
            logger.error("commit publish info fail")
            logger.exception(e)
            response = {"code": -1, "message": "创建失败!", "status": False}
    else:
        logger.error("add publish info fail, info is exist")
        response = {"code": -1, "message": "条目已存在!", "status": False}
    logger.debug("接口请求返回:" + json.dumps(response,ensure_ascii=False))
    return jsonify(response)



@publisher_bp.route('/publishing/update', methods=['POST'])
@require_access_token
def publishing_update(current_user):
    try:
        Publisher.query.filter_by(id=request.get_json()["id"]).update({'name': request.get_json()["name"]})
        # 提交更新到数据库（事务提交）
        db.session.commit()
        response = {"code": 0, "message": "保存成功!", "status": True}
        # audit_logger.debug("[{0}] [{1}] [{2}}] [更新出版社:{3}]".format(request.remote_addr,  current_user, model_name, request.get_json()['name']))
        insert_audit_log(request.remote_addr, current_user, model_name, '更新出版社: ' + request.get_json()["name"])
    except Exception as e:
        logger.error("update publish info fail")
        logger.exception(e)
        response = {"code": -1, "message": "保存失败!", "status": False}
    logger.debug("接口请求返回:" + json.dumps(response))
    return jsonify(response)

@publisher_bp.route('/publishing/query', methods=['POST'])
@require_access_token
def publishing_query(current_user):
    publish_list = []
    pageTotal = len(Publisher.query.all())
    if len(request.get_json())==0:
        query_result = Publisher.query.all()
    else:
        query_string = request.get_json()['query_string']
        # 指定分页信息查询数据
        if query_string == '':
            page = int(request.get_json()['page'])
            size = int(request.get_json()['size'])
            offset = (page - 1) * size
            query_result=Publisher.query.offset(offset).limit(size).all()
        # 指定关键字查询
        else:
            query_result = Publisher.query.filter((Publisher.name.contains(query_string))).all()
            pageTotal=len(query_result)
    for i in query_result:
        publish_name_dict = dict(i)
        publish_list.append(publish_name_dict)
    response = {"status": True, "message": "查询成功", "infos": publish_list, "pageTotal": pageTotal}
    logger.debug("接口请求返回:" + json.dumps(response,ensure_ascii=False))
    return jsonify(response)

@publisher_bp.route('/publishing/count', methods=['POST'])
@require_access_token
def publishing_count(current_user):
    count = len(Publisher.query.all())
    response = {"status": True, "message": "统计成功", "count": count}
    logger.debug("接口请求返回:" + json.dumps(response,ensure_ascii=False))
    return jsonify(response)


@publisher_bp.route('/publishing/delete', methods=['POST'])
@require_access_token
def publishing_delete(current_user):
    failed_item_ids = []
    if not isinstance(request.get_json()["id"],list):
        delete_ids=[request.get_json()["id"]]
    else:
        delete_ids = request.get_json()["id"]
    for publish_id in delete_ids:
        query_publish = Publisher.query.get(publish_id)
        # 判断该条目是否存在
        if query_publish is None:
            logger.error("delete {0} from table publish fail".format(request.get_json()))
            failed_item_ids.append(publish_id)
        else:
            try:
                db.session.delete(query_publish)  # 将对象放在缓存中准备删除
                db.session.commit()  # 提交事务，删除
                logger.success("delete {0} from table publish success".format(request.get_json()))
                # audit_logger.debug("[{0}] [{1}] [{2}] [删除出版社:{3}]".format(request.remote_addr,  current_user, model_name, request.get_json()['id']))
                insert_audit_log(request.remote_addr, current_user, model_name,'删除出版社: ' + str(request.get_json()["id"]))
            except Exception as e:
                logger.exception(e)
                db.session.rollback()
                failed_item_ids.append(publish_id)
                logger.error("delete {0}  from table publish fail".format(request.get_json()))
    if len(failed_item_ids) == 0:
        response = {"status": True, "code": 0, "message": '删除成功'}
    elif len(failed_item_ids) == len(delete_ids):
        response = {"status": False, "code": -2, "message": '删除失败'}
    else:
        response = {"status": True, "code": -1, "message": '部分条目删除失败'}
    logger.debug("接口请求返回:" + json.dumps(response,ensure_ascii=False))
    return jsonify(response)

