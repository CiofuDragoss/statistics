from app_flask import celery




result = celery.send_task('app.test', args=['test_session'])
result1 = celery.send_task('app.test', args=['test_session'])
result2 = celery.send_task('app.test', args=['test_session'])
print(result.get(timeout=10))

print(result1.get(timeout=10))

print(result2.get(timeout=10))

