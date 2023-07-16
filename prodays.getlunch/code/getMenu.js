import console from 'console'
import http from 'http'
import fail from 'fail'

export default function (input) {
  const { CheckDate, CheckType } = input

  console.log(CheckDate)
  console.log(CheckType)

  var urlDate

  // if (CheckDate == '오늘') {
  //   urlDate = '오늘'
  //   // console.log("set 오늘")
  // }
  if (CheckDate == '내일') {
    urlDate = '내일'
    // console.log("set 내일")
  }
  else {
    urlDate = '오늘'
    // console.log("else -> set 오늘")
  }

  var urlType
  
  // if (CheckType == '중식' || CheckType == '급식' || CheckType == '점심' || CheckType == '밥') {
  //   urlType = 'lunch'
  //   // console.log("set 중식")
  // }
  if (CheckType == '석식' || CheckType == '저녁'){
    urlType = 'dinner'
    // console.log("set 석식")
  }
  else {
    urlType = 'lunch'
    // console.log("else -> set 중식")
  }
  

  //API 요청 설정
  var URL = 'https://f7tu8l7xv1.execute-api.ap-northeast-2.amazonaws.com/' + urlType
  var Options = {
    format: 'json',
    returnHeaders: true,
    query: {
      date: urlDate
    }
  }
  
  //API 요청
  var response = http.getUrl(URL, Options)

  //메뉴 없음 (에러 코드 400)
  if (response.status == 400) {
    throw fail.checkedError('메뉴를 불러올 수 없습니다.','NoMenu',null)
  }

  //API 요청 정상적으로 처리
  return response.parsed
}
