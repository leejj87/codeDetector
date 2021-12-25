# codeDetector & flask api
1. generate api key
2. using "POST" method to get the code verified name
   ex) data = {'code': """public class Main {
  public static void main(String[] args) {
    System.out.println("Hello World");
  }
}""",'key':'asdfqwekafl1'}

  http://flaskServer_url/code_detector
