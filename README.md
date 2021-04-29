# hamonikr-upgrade-info

* 하모니카 릴리즈 업그레이드를 위한 정보를 모아놓은 패키지


## 버전 추가 방법
* 작성 방식은 릴리즈가 새로 나올 때 마다 /usr/share/hamonikr-upgrade-info 폴더에 업그레이드 정보 생성
* 릴리즈 폴더를 생성할 때에는 현재 사용하고 있는 OS 버전명을 소문자로 입력한다.
* 폴더안 내용들은 최신버전에 맞는 정보를 작성하여 추가한다.

## 실제 작업
* 해당 패키지는 단순히 업그레이드를 위한 정보를 모아놓았고
* 실제 mintreport 패키지에서 업그레이드 할 패키지가 존재하는지 확인
* mintupdate 패키지에서 실제로 업그레이드를 하는 방식이다.