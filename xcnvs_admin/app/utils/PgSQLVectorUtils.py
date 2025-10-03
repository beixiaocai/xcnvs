import psycopg2
from psycopg2 import sql as psycopg2_sql
# import numpy as np

class PgSQLVectorUtils():
    def __init__(self,logger,config):
        self.logger = logger
        if config.isEnableWenSou:
            # 配置开启了文搜功能
            print("PgSQLVectorUtils.__init__() 配置开启了文搜功能")
            self.logger.info("PgSQLVectorUtils.__init__() 配置开启了文搜功能")
            DB_CONFIG = {
                'host': '192.168.1.16',
                'port': 5432,
                'dbname': 'mydb',  # 替换为你的数据库名
                'user': 'root',  # 替换为你的用户名
                'password': 'pwd123456'  # 替换为你的密码
            }
            self.__conn = psycopg2.connect(**DB_CONFIG)
        else:
            # 配置未开启文搜功能
            print("PgSQLVectorUtils.__init__() 配置未开启文搜功能")
            self.logger.info("PgSQLVectorUtils.__init__() 配置未开启文搜功能")
            self.__conn = None

    def add_media_dim1024(self,media_code, content, embedding):
        cur = None
        try:
            cur = self.__conn.cursor()
            embedding = list(embedding)
            # print("add_media_dim1024()",type(embedding),embedding)

            # 插入数据
            insert_query = psycopg2_sql.SQL(
                "INSERT INTO media_dim1024 (media_code,content,embedding) VALUES (%s,%s,%s::vector)"
            )

            cur.execute(insert_query, (media_code, content, embedding))
            self.__conn.commit()

            # print("✅ 文档已成功存入 pgvector 数据库。")
            return True
        except Exception as e:
            msg = "add_media_dim1024() error:%s"%str(e)
            self.logger.error(msg)
            print(msg)
            self.__conn.rollback()
        finally:
            if cur:
                cur.close()
    def query_media_dim1024(self, query_embedding, top_k=3):
        cur = None
        try:
            cur = self.__conn.cursor()

            # 2. 在数据库中执行余弦相似度搜索
            # pgvector 中使用 <=> 表示余弦距离（越小越相似）
            search_query = psycopg2_sql.SQL("""
                SELECT media_code, content, embedding <-> %s::vector AS distance
                FROM media_dim1024
                ORDER BY distance
                LIMIT %s
            """)
            cur.execute(search_query, (query_embedding, top_k))
            results = cur.fetchall()

            # 返回结果
            # print("results:", type(results), len(results), results)
            data = []
            for result in results:
                distance = result[2]
                similarity_score = 1 - distance

                data.append({
                    "media_code": result[0],
                    "content": result[1],
                    "distance": distance,
                    "similarity_score": similarity_score
                })

            return data

        except Exception as e:
            msg = "query_media_dim1024() error:%s"%str(e)
            self.logger.error(msg)
            print(msg)
            return []
        finally:
            if cur:
                cur.close()