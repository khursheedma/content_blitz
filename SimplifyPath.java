import java.util.Stack;

public class SimplifyPath {

    public static void main(String[] args){
        // String path = "/home/";
        String path = "/home//foo/";
        // String path = "/home/user/Documents/../Pictures";
        System.out.println(simplify_path(path));
    }

    public static String simplify_path(String path){

        String[] tokens = path.split("/");

        Stack<String> st = new Stack<>();

        for (String token : tokens){
            if (token.equals("") || token.equals(".")){
                // do nothing (pass)
            } else if (token.equals("..")){
                if (st.size() > 0){
                    st.pop();
                }
            } else {
                st.push(token);
            }

        }
        return "/" + String.join("/", st);
    }

}
